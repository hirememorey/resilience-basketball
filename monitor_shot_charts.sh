#!/bin/bash
# Quick script to monitor shot chart collection progress

echo "Shot Chart Collection Status"
echo "============================"
echo ""

# Check if process is running
if pgrep -f "collect_shot_charts" > /dev/null; then
    echo "✅ Collection process is RUNNING"
    echo ""
else
    echo "❌ Collection process is NOT running"
    echo ""
fi

# Show recent log activity
echo "Recent activity (last 5 lines):"
tail -5 logs/shot_chart_collection.log 2>/dev/null || echo "  (No log file yet)"
echo ""

# Show progress
echo "To watch live progress:"
echo "  tail -f logs/shot_chart_collection.log"
echo ""
echo "To check completed files:"
echo "  python check_shot_chart_progress.py"

