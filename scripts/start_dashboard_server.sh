#!/bin/bash
# Script để start local server và mở dashboard

echo "🚀 Starting CheftAi Dashboard Server..."
echo ""

# Kill existing server on port 8000 if any
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start server in background
cd "$(dirname "$0")/.."
python3 -m http.server 8000 > /dev/null 2>&1 &
SERVER_PID=$!

# Wait a moment for server to start
sleep 2

# Check if server is running
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Server started on http://localhost:8000"
    echo ""
    echo "📊 Opening dashboard..."
    
    # Open dashboard in browser
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "http://localhost:8000/.mcp/dashboard.html"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "http://localhost:8000/.mcp/dashboard.html"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        start "http://localhost:8000/.mcp/dashboard.html"
    fi
    
    echo ""
    echo "✅ Dashboard opened!"
    echo ""
    echo "💡 Tips:"
    echo "   - Dashboard URL: http://localhost:8000/.mcp/dashboard.html"
    echo "   - Auto-refreshes every 5 seconds"
    echo "   - To stop server: kill $SERVER_PID"
    echo ""
    echo "Press Ctrl+C to stop the server..."
    
    # Wait for user interrupt
    trap "kill $SERVER_PID 2>/dev/null; exit" INT TERM
    wait $SERVER_PID
else
    echo "❌ Failed to start server"
    exit 1
fi

