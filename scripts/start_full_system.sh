#!/bin/bash
# Script để start toàn bộ system: API server, Dashboard server, và Monitor service

echo "🍳 Starting CheftAi Full Multi-Agent System"
echo "==========================================="
echo ""

cd "$(dirname "$0")/.."

# Kill existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f 'api_server.py' 2>/dev/null || true
pkill -f 'http.server.*8000' 2>/dev/null || true
pkill -f 'monitor_service.py' 2>/dev/null || true
pkill -f 'architect_server.py|backend_server.py|ui_server.py|qa_server.py' 2>/dev/null || true
sleep 2

# Start API server
echo "📡 Starting API Server (port 8001)..."
python3 .mcp/api_server.py > /tmp/api_server.log 2>&1 &
API_PID=$!

# Start Dashboard server
echo "📊 Starting Dashboard Server (port 8000)..."
python3 -m http.server 8000 > /tmp/dashboard_server.log 2>&1 &
HTTP_PID=$!

# Open all agent windows (optional - uncomment if needed)
echo "🪟 Opening agent windows..."
python3 .mcp/open_all_agent_windows.py > /tmp/open_windows.log 2>&1 &
sleep 3

# Start Monitor service
echo "👁️  Starting Monitor Service..."
if ! python3 -c "import watchdog" 2>/dev/null; then
    echo "   Installing watchdog..."
    pip3 install watchdog > /dev/null 2>&1
fi
python3 .mcp/monitor_service.py > /tmp/monitor_service.log 2>&1 &
MONITOR_PID=$!

# Start Agent Servers
echo "🤖 Starting Agent Servers..."
./scripts/start_agent_servers.sh > /tmp/agent_servers_startup.log 2>&1
AGENT_SERVERS_STARTED=$?

sleep 3

# Check all services
echo ""
echo "🔍 Checking services..."
if ps -p $API_PID > /dev/null && ps -p $HTTP_PID > /dev/null && ps -p $MONITOR_PID > /dev/null; then
    echo "✅ All services started!"
    echo ""
    echo "📊 Dashboard URLs:"
    echo "   - Enhanced: http://localhost:8000/.mcp/dashboard_enhanced.html"
    echo "   - Basic:    http://localhost:8000/.mcp/dashboard.html"
    echo ""
    echo "📡 API Server: http://localhost:8001"
    echo ""
    echo "👁️  Monitor Service: Watching shared_state.json"
    echo ""
    if [ $AGENT_SERVERS_STARTED -eq 0 ]; then
        echo "🤖 Agent Servers:"
        echo "   - Architect: http://localhost:8002"
        echo "   - Backend_AI_Dev: http://localhost:8003"
        echo "   - UI_UX_Dev: http://localhost:8004"
        echo "   - Testing_QA: http://localhost:8005"
        echo ""
    fi
    echo "📝 Log Files:"
    echo "   - API Server:    /tmp/api_server.log"
    echo "   - Dashboard:     /tmp/dashboard_server.log"
    echo "   - Monitor:       /tmp/monitor_service.log"
    echo "   - Auto-submit:   /tmp/auto_submit.log"
    echo ""
    echo "🔍 Monitor Logs:"
    echo "   tail -f /tmp/monitor_service.log"
    echo ""
    
    # Open dashboard
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "http://localhost:8000/.mcp/dashboard_enhanced.html"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "http://localhost:8000/.mcp/dashboard_enhanced.html"
    fi
    
    echo "💡 To stop all services:"
    echo "   kill $API_PID $HTTP_PID $MONITOR_PID"
    echo "   Or: pkill -f 'api_server|http.server|monitor_service|architect_server|backend_server|ui_server|qa_server'"
    echo ""
    echo "📋 Flow:"
    echo "   1. Ra lệnh cho Architect trong Cursor chat"
    echo "   2. Architect update shared_state.json với tasks PENDING"
    echo "   3. Monitor service tự động trigger worker agents"
    echo "   4. Workers làm việc và update status"
    echo ""
    
    # Wait
    trap "kill $API_PID $HTTP_PID $MONITOR_PID 2>/dev/null; exit" INT TERM
    wait
else
    echo "❌ Failed to start some services"
    echo "   Check logs for details"
    exit 1
fi

