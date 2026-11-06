@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Run install_desktop.bat first.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
where npm >nul 2>nul
if not errorlevel 1 (
  if exist package.json (
    call npm install
    call npm run build:css
    if errorlevel 1 goto failed
  )
) else (
  echo npm not found. If you changed Tailwind classes, install Node.js and rebuild static\css\output.css first.
)
pyinstaller --noconfirm --clean --onedir --windowed --name MyTradeMaster --contents-directory . --add-data "templates;templates" --add-data "static;static" --hidden-import main --hidden-import modules.models --collect-all uvicorn --collect-all webview --collect-all asyncpg desktop_app.py
if errorlevel 1 goto failed
copy /Y .env.example dist\MyTradeMaster\.env.example >nul
echo.
echo Build completed: dist\MyTradeMaster\MyTradeMaster.exe
echo Copy a correctly configured .env file beside the EXE before launching it.
pause
exit /b 0
:failed
echo Build failed. Review the error above.
pause
exit /b 1
