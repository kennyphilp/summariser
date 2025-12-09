#!/bin/zsh

# Script to start the Django summarizer application

cd /Users/kenny.w.philp/training/djangotest

source .venv/bin/activate

# Check for DEBUG parameter
if [[ "$1" == "DEBUG=False" ]]; then
    export DEBUG=False
else
    export DEBUG=True
fi

echo "Starting Django server in the background..."
python summarizer/manage.py runserver &