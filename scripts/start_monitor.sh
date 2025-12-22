#!/bin/bash
# Script để start monitor_service.py

echo "🚀 Starting Monitor Service..."
echo "=============================="
echo ""

cd "$(dirname "$0")/.."

# Check if monitor is already running
if pgrep -f "monitor_service.py" > /dev/null; then
    echo "⚠️  Monitor service is already running"
    echo "   PID: $(pgrep -f 'monitor_service.py')"
    echo ""
    read -p "Kill existing process and restart? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill -f "monitor_service.py"
        sleep 1
    else
        echo "✅ Keeping existing monitor service"
        exit 0
    fi
fi

# Check if watchdog is installed
if ! python3 -c "import watchdog" 2>/dev/null; then
    echo "📦 Installing watchdog..."
    pip3 install watchdog --quiet
    if [ $? -eq 0 ]; then
        echo "   ✅ watchdog installed"
    else
        echo "   ❌ Failed to install watchdog"
        echo "   Please install manually: pip3 install watchdog"
        exit 1
    fi
fi

# Start monitor service in background
echo "📡 Starting monitor service..."
python3 .mcp/monitor_service.py > /tmp/monitor_service.log 2>&1 &
MONITOR_PID=$!

sleep 2

# Check if started successfully
if ps -p $MONITOR_PID > /dev/null; then
    echo "✅ Monitor service started!"
    echo "   PID: $MONITOR_PID"
    echo "   Logs: /tmp/monitor_service.log"
    echo ""
    echo "💡 To stop: kill $MONITOR_PID"
    echo "   Or: pkill -f monitor_service.py"
    echo ""
    echo "📋 Monitor will:"
    echo "   - Watch shared_state.json for changes"
    echo "   - Auto-trigger agents when tasks are PENDING"
    echo "   - Update task status to IN_PROGRESS"
    echo ""
    echo "🔍 To view logs: tail -f /tmp/monitor_service.log"
else
    echo "❌ Failed to start monitor service"
    echo "   Check logs: /tmp/monitor_service.log"
    exit 1
fi

