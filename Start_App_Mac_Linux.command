#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "============================================"
echo " AI Ethics Readiness Tool - Local Launcher"
echo "============================================"
echo ""

PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "Python was not found on this computer."
    echo "Please install it from https://www.python.org/downloads/"
    read -p "Press Enter to close..."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Setting up the app for the first time, this may take a minute..."
    "$PYTHON_BIN" -m venv venv
fi

source venv/bin/activate

echo "Installing required packages..."
pip install --quiet -r requirements.txt

if [ ! -f "db.sqlite3" ]; then
    echo "Setting up the database..."
    python manage.py migrate
    python manage.py load_rules
fi

echo ""
echo "Starting the app..."
echo "Your browser will open automatically. If it doesn't, go to:"
echo "  http://127.0.0.1:8000/"
echo ""
echo "Leave this window open while using the app."
echo "Press Ctrl+C to stop the app."
echo ""

# Open the browser after a short delay, once the server is likely up
( sleep 2 && (open http://127.0.0.1:8000/ 2>/dev/null || xdg-open http://127.0.0.1:8000/ 2>/dev/null) ) &

python manage.py runserver
