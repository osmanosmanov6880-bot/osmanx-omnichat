"""OSMANX OMNICHAT safe backups for offline SQLite and Docker PostgreSQL.

Security properties:
* SQLite uses sqlite3.backup() rather than copying a live WAL database.
* PostgreSQL uses pg_dump's custom format and checks BOTH dump and pg_restore.
* Incomplete files are never published as backups.
* Every backup carries a SHA256 manifest; verify before restore.
* SQLite restore refuses to overwrite any existing path.
* No secrets or plaintext database rows are printed.

Backups contain sensitive customer data. Encrypt and store them offsite.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import sqlite3
import subprocess
import sys
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
CHUNK = 1024 * 1024
REQUIRED_TABLES = {"organizations", "conversations", "messages"}


class BackupError(RuntimeError):
    pass


def _hash(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as inp:
        while chunk := inp.read(CHUNK):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def _private_directory(path: Path) -> Path:
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink():
        raise BackupError("Backup directory must not be a symbolic link")
    if os.name == "posix":
        os.chmod(path, 0o700)
    return path


def _temp_file(path: Path):
    return path.with_name(path.name + ".partial-" + secrets.token_hex(8))


def _metadata(path: Path, engine: str, extra: dict | None = None) -> dict:
    sha, size = _hash(path)
    metadata = {
        "format": "osmanx-backup-manifest-v1",
        "engine": engine,
        "file": path.name,
        "sha256": sha,
        "size_bytes": size,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    if extra:
        metadata.update(extra)
    return metadata


def _manifest_file(path: Path) -> Path:
    return path.with_name(path.name + ".manifest.json")


def _write_manifest(path: Path, metadata: dict) -> Path:
    manifest = _manifest_file(path)
    temp = _temp_file(manifest)
    try:
        with temp.open("x", encoding="utf-8") as out:
            os.chmod(temp, 0o600)
            json.dump(metadata, out, ensure_ascii=True, indent=2, sort_keys=True)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(temp, manifest)
        return manifest
    finally:
        temp.unlink(missing_ok=True)


def _sqlite_connect_readonly(path: Path):
    uri = "file:" + quote(path.resolve().as_posix(), safe="/:") + "?mode=ro"
    return sqlite3.connect(uri, uri=True, timeout=15)


def _sqlite_check(path: Path) -> dict:
    try:
        with _sqlite_connect_readonly(path) as db:
            status = db.execute("PRAGMA integrity_check").fetchone()
            if not status or status[0] != "ok":
                raise BackupError("SQLite integrity check failed")
            tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            missing = REQUIRED_TABLES - tables
            if missing:
                raise BackupError("Not an OMNICHAT database (missing expected tables)")
            version = None
            if "alembic_version" in tables:
                rows = db.execute("SELECT version_num FROM alembic_version LIMIT 2").fetchall()
                version = rows[0][0] if len(rows) == 1 else None
            return {"schema_revision": version, "schema_table_count": len(tables)}
    except sqlite3.DatabaseError as exc:
        raise BackupError("SQLite database cannot be read or is corrupt") from exc


def sqlite_backup(source: Path, directory: Path) -> Path:
    source = Path(source)
    if not source.is_file():
        raise BackupError("Local SQLite database does not exist; start OMNICHAT first")
    if source.is_symlink():
        raise BackupError("Refusing to back up a symlink database")
    destdir = _private_directory(Path(directory))
    name = "omnichat-sqlite-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = destdir / (name + "-" + secrets.token_hex(4) + ".sqlite3")
    temp = _temp_file(path)
    try:
        descriptor = os.open(temp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(descriptor)
        with _sqlite_connect_readonly(source) as src:
            with sqlite3.connect(temp) as dst:
                src.backup(dst, pages=128, sleep=0.05)
                dst.commit()
        os.chmod(temp, 0o600)
        info = _sqlite_check(temp)
        os.replace(temp, path)
        try:
            _write_manifest(path, _metadata(path, "sqlite", info))
        except Exception:
            path.unlink(missing_ok=True)
            raise
        return path
    finally:
        temp.unlink(missing_ok=True)


def _validate_manifest(path: Path, expected: str | None = None) -> dict:
    if not path.is_file() or path.is_symlink():
        raise BackupError("Backup file missing or not a regular file")
    manifest = _manifest_file(path)
    if not manifest.is_file() or manifest.is_symlink():
        raise BackupError("Backup manifest is missing")
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise BackupError("Backup manifest is invalid") from exc
    if data.get("format") != "osmanx-backup-manifest-v1" or data.get("file") != path.name:
        raise BackupError("Backup manifest does not match this file")
    if expected and data.get("engine") != expected:
        raise BackupError("Backup engine does not match requested operation")
    checksum, size = _hash(path)
    if checksum != data.get("sha256") or size != data.get("size_bytes"):
        raise BackupError("Backup checksum mismatch; do not restore")
    return data


def sqlite_verify(path: Path) -> dict:
    data = _validate_manifest(Path(path), "sqlite")
    state = _sqlite_check(Path(path))
    if data.get("schema_revision") != state["schema_revision"]:
        raise BackupError("Schema revision differs from manifest")
    return data


def sqlite_restore_new(backup_path: Path, target: Path) -> Path:
    """Only restore to a NEW file; never replace a live database."""
    metadata = sqlite_verify(backup_path)
    target = Path(target)
    if target == Path(backup_path) or not target.parent.is_dir():
        raise BackupError("Choose a new target in an existing directory")
    try:
        descriptor = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise BackupError("Refusing to overwrite an existing database") from exc
    try:
        with os.fdopen(descriptor, "wb") as dst, Path(backup_path).open("rb") as src:
            shutil.copyfileobj(src, dst, CHUNK)
            dst.flush()
            os.fsync(dst.fileno())
        checksum, size = _hash(target)
        if checksum != metadata["sha256"] or size != metadata["size_bytes"]:
            raise BackupError("Restored data does not match the verified backup")
        _sqlite_check(target)
        return target
    except BaseException:
        target.unlink(missing_ok=True)
        raise


def _compose_command(operation: str) -> list[str]:
    if operation == "dump":
        command = 'PGPASSWORD="$POSTGRES_PASSWORD" exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner --no-acl'
    elif operation == "list":
        command = 'exec pg_restore -l'
    else:
        raise BackupError("Unsupported database command")
    return ["docker", "compose", "exec", "-T", "postgres", "sh", "-c", command]


def _pg_restore_list(path: Path) -> None:
    try:
        with path.open("rb") as stream:
            result = subprocess.run(_compose_command("list"), cwd=ROOT, stdin=stream,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BackupError("pg_restore inspection could not finish") from exc
    if result.returncode != 0:
        raise BackupError("pg_restore rejected this backup")


def postgres_backup(directory: Path) -> Path:
    """Require Docker and create a verified pg_dump custom archive; no restore."""
    destdir = _private_directory(Path(directory))
    name = "omnichat-postgres-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = destdir / (name + "-" + secrets.token_hex(4) + ".dump")
    temp = _temp_file(path)
    try:
        descriptor = os.open(temp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(descriptor, "wb") as out:
            try:
                result = subprocess.run(_compose_command("dump"), cwd=ROOT,
                                        stdout=out, stderr=subprocess.PIPE, timeout=3600)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise BackupError("pg_dump could not start or finish") from exc
            out.flush()
            os.fsync(out.fileno())
        if result.returncode != 0:
            raise BackupError("pg_dump failed; no backup was published")
        with temp.open("rb") as contents:
            if contents.read(5) != b"PGDMP":
                raise BackupError("pg_dump returned an invalid custom-format archive")
        _pg_restore_list(temp)
        os.replace(temp, path)
        try:
            _write_manifest(path, _metadata(path, "postgresql"))
        except Exception:
            path.unlink(missing_ok=True)
            raise
        return path
    finally:
        temp.unlink(missing_ok=True)


def postgres_verify(path: Path) -> dict:
    data = _validate_manifest(Path(path), "postgresql")
    with Path(path).open("rb") as stream:
        if stream.read(5) != b"PGDMP":
            raise BackupError("Invalid PostgreSQL archive header")
    _pg_restore_list(Path(path))
    return data


def _sqlite_revision_fast(path: Path) -> str | None:
    """Read only metadata on normal startups; full integrity belongs to backups."""
    try:
        with _sqlite_connect_readonly(path) as connection:
            tables = {row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
            if REQUIRED_TABLES - tables:
                raise BackupError("Not an OMNICHAT database (missing expected tables)")
            if "alembic_version" not in tables:
                return None
            revisions = connection.execute("SELECT version_num FROM alembic_version LIMIT 2").fetchall()
            return revisions[0][0] if len(revisions) == 1 else None
    except sqlite3.DatabaseError as exc:
        raise BackupError("SQLite database cannot be read or is corrupt") from exc


def before_local_migration(database_url: str, directory: Path, expected_revisions: set[str]) -> Path | None:
    """Snapshot an existing SQLite DB only if an upgrade would change its schema.

    No source database is opened for writes. A broken DB aborts migration rather
    than allowing Alembic to destroy the user's last copy.
    """
    from sqlalchemy.engine import make_url
    try:
        url = make_url(database_url)
    except Exception as exc:
        raise BackupError("DATABASE_URL cannot be parsed") from exc
    if url.drivername != "sqlite" or not url.database or url.database == ":memory:":
        return None  # Docker/Postgres must use its independent backup policy.
    source = Path(url.database)
    if not source.is_file():
        return None  # Brand new installation, no data to protect.
    revision = _sqlite_revision_fast(source)
    current = {revision} if revision else set()
    if current == expected_revisions:
        return None  # No migration, avoid redundant sensitive files.
    return sqlite_backup(source, directory)


def _expected_alembic_heads() -> set[str]:
    from alembic.config import Config
    from alembic.script import ScriptDirectory
    config = Config(str(ROOT / "backend" / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "backend" / "alembic"))
    return set(ScriptDirectory.from_config(config).get_heads())


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Safe OMNICHAT backups. Never overwrite a live database.")
    operations = parser.add_subparsers(dest="mode", required=True)
    sqlite = operations.add_parser("sqlite-backup", help="Create consistent SQLite snapshot")
    sqlite.add_argument("--database", type=Path, default=Path("omnichat.db"))
    sqlite.add_argument("--directory", type=Path, default=Path("backups"))
    for mode in ("sqlite-verify", "postgres-verify"):
        command = operations.add_parser(mode)
        command.add_argument("--file", type=Path, required=True)
    restore = operations.add_parser("sqlite-restore-new", help="Restore to a new file only")
    restore.add_argument("--file", type=Path, required=True)
    restore.add_argument("--target", type=Path, required=True)
    pg = operations.add_parser("postgres-backup", help="Docker custom-format pg_dump")
    pg.add_argument("--directory", type=Path, default=Path("backups"))
    before = operations.add_parser("before-local-migration", help="Back up SQLite if schema upgrade is pending")
    before.add_argument("--directory", type=Path, default=Path("backups"))
    args = parser.parse_args()
    try:
        if args.mode == "sqlite-backup":
            path = sqlite_backup(args.database, args.directory)
            print("Backup created and verified:", path)
        elif args.mode == "sqlite-verify":
            print("SQLite backup verified:", sqlite_verify(args.file)["file"])
        elif args.mode == "sqlite-restore-new":
            print("Restored to new database:", sqlite_restore_new(args.file, args.target))
        elif args.mode == "postgres-backup":
            path = postgres_backup(args.directory)
            print("Backup created and inspected:", path)
        elif args.mode == "postgres-verify":
            print("PostgreSQL archive verified:", postgres_verify(args.file)["file"])
        elif args.mode == "before-local-migration":
            from dotenv import load_dotenv
            load_dotenv(ROOT / ".env", override=False)
            url = os.getenv("DATABASE_URL", "sqlite:///./omnichat.db")
            backup = before_local_migration(url, args.directory, _expected_alembic_heads())
            print("Before-migration backup:", backup if backup else "not needed (or non-SQLite)")
    except BackupError as exc:
        print("BACKUP ERROR:", str(exc), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    _cli()
