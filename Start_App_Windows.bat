@echo off
setlocal

echo ============================================
echo  AI Ethics Readiness Tool - Local Launcher
echo ============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found on this computer.
    echo Please install it from https://www.python.org/downloads/
    echo During install, make sure to tick "Add Python to PATH".
    pause
    exit /b 1
)

cd /d "%~dp0"

if not exist "venv" (
    echo Setting up the app for the first time, this may take a minute...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing required packages...
pip install --quiet -r requirements.txt

if not exist "db.sqlite3" (
    echo Setting up the database...
    python manage.py migrate
    python manage.py load_rules
)

echo.
echo Starting the app...
echo Your browser will open automatically. If it doesn't, go to:
echo   http://localhost:8000/
echo.
echo Leave this window open while using the app.
echo Close this window to stop the app.
echo.

start "" http://localhost:8000/
python manage.py runserver

pause
