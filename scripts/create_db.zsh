#!/bin/zsh

# Script to create database tables using SQL script

DB_PATH="/Users/kenny.w.philp/training/djangotest/summarizer/db.sqlite3"
SQL_FILE="/Users/kenny.w.philp/training/djangotest/scripts/create_tables.sql"

if [ -f "$DB_PATH" ]; then
    echo "Database already exists. Skipping table creation."
else
    echo "Creating database tables..."
    sqlite3 "$DB_PATH" < "$SQL_FILE"
    echo "Tables created successfully."
fi