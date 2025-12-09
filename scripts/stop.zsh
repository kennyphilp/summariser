#!/bin/zsh

# Script to stop the Django summarizer application

# Check if any Django server is running
if pgrep -f "manage.py runserver" > /dev/null; then
    echo "Stopping Django server..."
    pkill -f "manage.py runserver"
    echo "Django server stopped."
else
    echo "No running Django server found."
fi