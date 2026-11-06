@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher ^(py^) was not found. Install Python 3.11 or 3.12 and enable Add Python to PATH.
  pause
  exit /b 1
)
if not exist .venv (
  py -3 -m venv .venv
  if errorlevel 1 goto failed
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r desktop_requirements.txt
if errorlevel 1 goto failed
if not exist .env copy .env.example .env
 echo.
echo Dependencies installed. Edit .env, create the PostgreSQL database, then run run_desktop.bat.
pause
exit /b 0
:failed
echo Installation failed. Review the error above.
pause
exit /b 1
