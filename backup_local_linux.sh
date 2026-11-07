#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 scripts/backup_safety.py sqlite-backup --database omnichat.db --directory backups
printf 'Store the new backup encrypted and offsite.\n'
