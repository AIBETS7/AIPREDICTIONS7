#!/bin/bash

# Script to setup cron job for daily picks
# This script will add a cron job to run daily picks at 8:00 AM

echo "🔧 Setting up automated daily picks..."

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/daily_pick_automated.py"

# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Error: daily_pick_automated.py not found in $SCRIPT_DIR"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/logs"

# Create the cron job entry (runs at 8:00 AM every day)
CRON_JOB="0 8 * * * cd $SCRIPT_DIR && /usr/bin/python3 $PYTHON_SCRIPT >> $SCRIPT_DIR/logs/cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "daily_pick_automated.py"; then
    echo "⚠️ Cron job already exists. Removing old entry..."
    # Remove existing cron job
    crontab -l 2>/dev/null | grep -v "daily_pick_automated.py" | crontab -
fi

# Add the new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job added successfully!"
    echo "📅 Daily picks will run at 8:00 AM every day"
    echo "📁 Logs will be saved to: $SCRIPT_DIR/logs/"
    echo ""
    echo "Current cron jobs:"
    crontab -l
else
    echo "❌ Failed to add cron job"
    exit 1
fi

echo ""
echo "🎯 To test the system manually, run:"
echo "   cd $SCRIPT_DIR && python3 daily_pick_automated.py"
echo ""
echo "📋 To view cron logs:"
echo "   tail -f $SCRIPT_DIR/logs/cron.log"
echo ""
echo "🗑️ To remove the cron job:"
echo "   crontab -e"
echo "   (then delete the line with daily_pick_automated.py)" 