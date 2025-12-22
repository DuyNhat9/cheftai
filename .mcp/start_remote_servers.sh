#!/bin/bash
# Script để start API và Dashboard servers cho remote access
# Usage: ./start_remote_servers.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

echo "🚀 Starting servers for remote access..."

# Kill existing servers
pkill -f "api_server.py" 2>/dev/null
pkill -f "dashboard_server.py" 2>/dev/null
sleep 1

# Start API server
echo "📡 Starting API server on port 8001..."
python3 .mcp/api_server.py > /tmp/api_server.log 2>&1 &
API_PID=$!
echo "   API Server PID: $API_PID"

# Start Dashboard server
echo "🌐 Starting Dashboard server on port 8000..."
python3 .mcp/dashboard_server.py > /tmp/dashboard_server.log 2>&1 &
DASHBOARD_PID=$!
echo "   Dashboard Server PID: $DASHBOARD_PID"

sleep 2

# Check if servers are running
if ps -p $API_PID > /dev/null && ps -p $DASHBOARD_PID > /dev/null; then
    echo ""
    echo "✅ Servers started successfully!"
    echo ""
    echo "📡 Access from local machine:"
    echo "   Dashboard: http://localhost:8000/.mcp/dashboard_enhanced.html"
    echo "   API: http://localhost:8001/api/state"
    echo ""
    echo "🌐 Access from remote machine (after SSH port forwarding):"
    echo "   Dashboard: http://localhost:8000/.mcp/dashboard_enhanced.html"
    echo "   API: http://localhost:8001/api/state"
    echo ""
    echo "📋 To stop servers:"
    echo "   pkill -f api_server.py"
    echo "   pkill -f dashboard_server.py"
    echo ""
    echo "📊 View logs:"
    echo "   tail -f /tmp/api_server.log"
    echo "   tail -f /tmp/dashboard_server.log"
else
    echo "❌ Failed to start servers. Check logs:"
    echo "   tail /tmp/api_server.log"
    echo "   tail /tmp/dashboard_server.log"
    exit 1
fi

