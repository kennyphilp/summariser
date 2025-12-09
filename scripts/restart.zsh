#!/bin/zsh

# Script to restart the Django summarizer application

echo "Checking for running Django server..."

# Check if any Django server is running
if pgrep -f "manage.py runserver" > /dev/null; then
    echo "Stopping Django server..."
    pkill -f "manage.py runserver"
    sleep 2  # Wait for it to shut down
    echo "Django server stopped."
else
    echo "No running Django server found."
fi

echo "Starting Django server..."
cd /Users/kenny.w.philp/training/djangotest
./scripts/start.zsh