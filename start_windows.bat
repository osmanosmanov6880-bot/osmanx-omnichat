@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python 3.12+ is required. Install Python before running OMNICHAT.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
  if errorlevel 1 goto failure
)
if not exist ".env" (
  copy /Y ".env.example" ".env" >nul
)
call ".venv\Scripts\activate.bat"
python -m pip install -r backend\requirements.txt
if errorlevel 1 goto failure
set PYTHONPATH=backend
python scripts\backup_safety.py before-local-migration --directory backups
if errorlevel 1 goto failure
python -m alembic -c backend\alembic.ini upgrade head
if errorlevel 1 goto failure
echo OSMANX OMNICHAT is starting at http://127.0.0.1:8000
start "" http://127.0.0.1:8000
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
exit /b %errorlevel%
:failure
echo Installation or database migration failed. Inspect the error above.
pause
exit /b 1
