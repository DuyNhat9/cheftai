#!/bin/bash
# Script để mở Multi-Agent Dashboard với local server

echo "🚀 Opening CheftAi Multi-Agent Dashboard..."
echo ""

# Check if server is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "✅ Server already running on port 8000"
    SERVER_RUNNING=true
else
    echo "🔄 Starting local server..."
    cd "$(dirname "$0")/.."
    
    # Start server in background
    python3 -m http.server 8000 > /tmp/dashboard_server.log 2>&1 &
    SERVER_PID=$!
    sleep 2
    
    # Check if server started
    if ps -p $SERVER_PID > /dev/null 2>&1; then
        echo "✅ Server started (PID: $SERVER_PID)"
        SERVER_RUNNING=true
    else
        echo "❌ Failed to start server"
        echo "💡 Try running: python3 -m http.server 8000"
        exit 1
    fi
fi

# Open dashboard in browser
DASHBOARD_URL="http://localhost:8000/.mcp/dashboard.html"

if [[ "$OSTYPE" == "darwin"* ]]; then
    open "$DASHBOARD_URL"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "$DASHBOARD_URL"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    start "$DASHBOARD_URL"
else
    echo "⚠️  Unknown OS. Please open manually: $DASHBOARD_URL"
    exit 1
fi

echo ""
echo "✅ Dashboard opened in browser!"
echo "📊 URL: $DASHBOARD_URL"
echo ""
echo "💡 Tips:"
echo "   - Dashboard auto-refreshes every 5 seconds"
echo "   - Click refresh button to manual refresh"
echo "   - Filter tasks by status (All/Completed/In Progress/Pending)"
echo ""
echo "⚠️  Keep this terminal open to keep server running"
echo "   Press Ctrl+C to stop server"
echo ""

