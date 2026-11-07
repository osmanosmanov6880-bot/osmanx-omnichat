"""Local backup consistency and failure-safety regression tests (no live services)."""
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from types import SimpleNamespace

import pytest
import importlib.util
module_path = Path(__file__).resolve().parents[2] / "scripts" / "backup_safety.py"
spec = importlib.util.spec_from_file_location("omnichat_backup_safety", module_path)
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)


def sample_database(path):
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("CREATE TABLE organizations(id TEXT PRIMARY KEY, name TEXT)")
    connection.execute("CREATE TABLE conversations(id TEXT PRIMARY KEY)")
    connection.execute("CREATE TABLE messages(id TEXT PRIMARY KEY, body TEXT)")
    connection.execute("CREATE TABLE alembic_version(version_num TEXT)")
    connection.execute("INSERT INTO organizations VALUES ('org-1','Test Company')")
    connection.execute("INSERT INTO alembic_version VALUES ('revision_v1')")
    connection.commit()
    return connection


def test_hot_wal_sqlite_snapshot_is_consistent_and_restorable(tmp_path):
    database = tmp_path / "omnichat.db"
    conn = sample_database(database)
    # Row may remain in WAL while source is open; copying .db alone is unsafe.
    conn.execute("INSERT INTO messages VALUES ('m-1', 'Saved while online')")
    conn.commit()
    archive = bs.sqlite_backup(database, tmp_path / "backups")
    assert archive.is_file() and bs._manifest_file(archive).is_file()
    manifest = bs.sqlite_verify(archive)
    assert manifest["engine"] == "sqlite"
    assert manifest["schema_revision"] == "revision_v1"
    if os.name == "posix":
        assert archive.stat().st_mode & 0o077 == 0
    restored = bs.sqlite_restore_new(archive, tmp_path / "recovery-test.db")
    with sqlite3.connect(restored) as check:
        assert check.execute("SELECT body FROM messages").fetchone()[0] == "Saved while online"
        assert check.execute("SELECT name FROM organizations").fetchone()[0] == "Test Company"
    conn.close()


def test_tampering_rejected_before_any_restore(tmp_path):
    db = tmp_path / "data.db"
    conn = sample_database(db)
    conn.close()
    archive = bs.sqlite_backup(db, tmp_path / "safe")
    with archive.open("ab") as contents:
        contents.write(b"MALICIOUS-TAMPER")
    with pytest.raises(bs.BackupError, match="checksum mismatch"):
        bs.sqlite_verify(archive)
    target = tmp_path / "new.db"
    with pytest.raises(bs.BackupError):
        bs.sqlite_restore_new(archive, target)
    assert not target.exists()


def test_never_overwrite_database_or_symlink_source(tmp_path):
    db = tmp_path / "source.db"
    conn = sample_database(db)
    conn.close()
    archive = bs.sqlite_backup(db, tmp_path / "safe")
    original = db.read_bytes()
    with pytest.raises(bs.BackupError, match="overwrite"):
        bs.sqlite_restore_new(archive, db)
    assert db.read_bytes() == original
    if hasattr(os, "symlink"):
        link = tmp_path / "linked.db"
        link.symlink_to(db)
        with pytest.raises(bs.BackupError, match="symlink"):
            bs.sqlite_backup(link, tmp_path / "safe")


def test_sqlite_backup_rejects_missing_and_broken_schema(tmp_path):
    with pytest.raises(bs.BackupError, match="does not exist"):
        bs.sqlite_backup(tmp_path / "missing.db", tmp_path / "safe")
    empty = tmp_path / "empty.db"
    sqlite3.connect(empty).close()
    with pytest.raises(bs.BackupError, match="Not an OMNICHAT database"):
        bs.sqlite_backup(empty, tmp_path / "safe")
    assert not list((tmp_path / "safe").glob("*.partial-*"))
    assert not list((tmp_path / "safe").glob("*.sqlite3"))


def test_postgresql_failed_dump_never_publish_partial(tmp_path, monkeypatch):
    def broken_run(command, **kwargs):
        if "pg_dump" in command[-1]:
            kwargs["stdout"].write(b"PGDMP-partial")
        return SimpleNamespace(returncode=7)
    monkeypatch.setattr(bs.subprocess, "run", broken_run)
    with pytest.raises(bs.BackupError, match="pg_dump failed"):
        bs.postgres_backup(tmp_path / "pgsafe")
    assert not any((tmp_path / "pgsafe").iterdir())


def test_postgres_verified_custom_dump_and_tamper(tmp_path, monkeypatch):
    calls = []
    def fake_run(command, **kwargs):
        calls.append(command[-1])
        if "pg_dump" in command[-1]:
            kwargs["stdout"].write(b"PGDMP" + b"TEST-DUMP-CONTENTS")
        else:
            assert kwargs["stdin"].read(5) == b"PGDMP"
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(bs.subprocess, "run", fake_run)
    archive = bs.postgres_backup(tmp_path / "pgsafe")
    assert archive.suffix == ".dump"
    manifest = bs.postgres_verify(archive)
    assert manifest["engine"] == "postgresql"
    assert any("pg_dump" in c for c in calls)
    assert any("pg_restore" in c for c in calls)
    with archive.open("ab") as contents:
        contents.write(b"changed")
    with pytest.raises(bs.BackupError, match="checksum mismatch"):
        bs.postgres_verify(archive)


def test_pg_restore_list_rejection_blocks_publication(tmp_path, monkeypatch):
    def fake_run(command, **kwargs):
        if "pg_dump" in command[-1]:
            kwargs["stdout"].write(b"PGDMP" + b"INVALID")
            return SimpleNamespace(returncode=0)
        return SimpleNamespace(returncode=1)
    monkeypatch.setattr(bs.subprocess, "run", fake_run)
    with pytest.raises(bs.BackupError, match="pg_restore rejected"):
        bs.postgres_backup(tmp_path / "pgsafe")
    assert not list((tmp_path / "pgsafe").iterdir())


def test_release_archive_never_contains_database_or_backups(tmp_path):
    root = Path(__file__).resolve().parents[2]
    private = root / "backups" / "not-for-release.sqlite3"
    private.parent.mkdir(exist_ok=True)
    secret = os.urandom(80)
    private.write_bytes(secret)
    out = tmp_path / "release.zip"
    try:
        result = subprocess.run([sys.executable, "scripts/build_release.py", str(out)],
            cwd=root, capture_output=True, text=True, timeout=35)
        assert result.returncode == 0, result.stderr
        from zipfile import ZipFile
        with ZipFile(out) as archive:
            names = archive.namelist()
            assert not any("/backups/" in n or n.endswith((".dump", ".sqlite3", ".sql.gz")) for n in names)
            assert not any("/.env" in n and not n.endswith(".env.example") for n in names)
            assert not any(secret in archive.read(n) for n in names)
    finally:
        private.unlink(missing_ok=True)


def test_pre_upgrade_backup_only_if_old_revision_exists(tmp_path):
    original = tmp_path / "before.db"
    conn = sample_database(original)
    conn.close()
    backups = tmp_path / "backups"
    old = bs.before_local_migration("sqlite:///" + str(original), backups, {"new_head"})
    assert old is not None and bs.sqlite_verify(old)["schema_revision"] == "revision_v1"
    assert bs.before_local_migration("sqlite:///" + str(original), backups, {"revision_v1"}) is None
    assert len(list(backups.glob("*.sqlite3"))) == 1


def test_pre_upgrade_skip_missing_database_and_postgres(tmp_path):
    backups = tmp_path / "backups"
    missing = tmp_path / "does-not-exist.db"
    assert bs.before_local_migration("sqlite:///" + str(missing), backups, {"head"}) is None
    assert bs.before_local_migration("postgresql://localhost/production", backups, {"head"}) is None
    assert not backups.exists()
