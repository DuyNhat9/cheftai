#!/bin/bash
# Script để start cả HTTP server và API server cho dashboard

echo "🚀 Starting CheftAi Dashboard System..."
echo ""

cd "$(dirname "$0")/.."

# Kill existing servers
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8001 | xargs kill -9 2>/dev/null || true

# Start HTTP server (port 8000) for dashboard
echo "📊 Starting HTTP server (port 8000)..."
python3 -m http.server 8000 > /tmp/dashboard_http.log 2>&1 &
HTTP_PID=$!

# Start API server (port 8001) for updates
echo "📡 Starting API server (port 8001)..."
python3 .mcp/api_server.py > /tmp/dashboard_api.log 2>&1 &
API_PID=$!

sleep 2

# Check servers
if ps -p $HTTP_PID > /dev/null && ps -p $API_PID > /dev/null; then
    echo "✅ Both servers started!"
    echo ""
    echo "📊 Dashboard URLs:"
    echo "   - Enhanced: http://localhost:8000/.mcp/dashboard_enhanced.html"
    echo "   - Basic: http://localhost:8000/.mcp/dashboard.html"
    echo ""
    echo "📡 API Server: http://localhost:8001"
    echo ""
    
    # Open dashboard
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "http://localhost:8000/.mcp/dashboard_enhanced.html"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "http://localhost:8000/.mcp/dashboard_enhanced.html"
    fi
    
    echo "💡 To stop servers: kill $HTTP_PID $API_PID"
    echo "   Or press Ctrl+C"
    echo ""
    
    # Wait
    trap "kill $HTTP_PID $API_PID 2>/dev/null; exit" INT TERM
    wait
else
    echo "❌ Failed to start servers"
    exit 1
fi

