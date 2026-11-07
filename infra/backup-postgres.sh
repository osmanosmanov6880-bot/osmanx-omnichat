#!/bin/sh
# Docker PostgreSQL backup. Fails closed on pg_dump or pg_restore errors.
set -eu
cd "$(dirname "$0")/.."
exec python3 scripts/backup_safety.py postgres-backup --directory backups
