@echo off
setlocal
cd /d "%~dp0"
python scripts\backup_safety.py sqlite-backup --database omnichat.db --directory backups
if errorlevel 1 (
  echo Backup failed. Existing data was not changed.
  exit /b 1
)
echo Keep this backup encrypted and outside the computer.
pause
