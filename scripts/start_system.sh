#!/bin/bash
# Start toàn bộ hệ thống CheftAi: API server, Dashboard server, và Log monitor

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

echo "🍳 CheftAi Multi-Agent System - Starting..."
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Kill existing servers
echo -e "${YELLOW}Cleaning up existing servers...${NC}"
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
sleep 1

# Start API Server
echo -e "${BLUE}📡 Starting API Server (port 8001)...${NC}"
python3 .mcp/api_server.py > /tmp/api_server.log 2>&1 &
API_PID=$!
sleep 2

# Start Dashboard Server
echo -e "${BLUE}📊 Starting Dashboard Server (port 8000)...${NC}"
python3 -m http.server 8000 > /tmp/dashboard_server.log 2>&1 &
HTTP_PID=$!
sleep 2

# Check if servers are running
if ps -p $API_PID > /dev/null && ps -p $HTTP_PID > /dev/null; then
    echo ""
    echo -e "${GREEN}✅ All servers started successfully!${NC}"
    echo ""
    echo "📊 Dashboard URLs:"
    echo "   - Enhanced: http://localhost:8000/.mcp/dashboard_enhanced.html"
    echo "   - Basic:    http://localhost:8000/.mcp/dashboard.html"
    echo ""
    echo "📡 API Server: http://localhost:8001"
    echo ""
    echo "📝 Log Files:"
    echo "   - API Server:    /tmp/api_server.log"
    echo "   - Dashboard:     /tmp/dashboard_server.log"
    echo "   - Auto-submit:   /tmp/auto_submit.log"
    echo ""
    echo "🔍 Monitor Logs:"
    echo "   ./scripts/monitor_logs.sh"
    echo "   ./scripts/quick_logs.sh api"
    echo ""
    
    # Open dashboard
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${BLUE}🌐 Opening dashboard in browser...${NC}"
        open "http://localhost:8000/.mcp/dashboard_enhanced.html"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "http://localhost:8000/.mcp/dashboard_enhanced.html"
    fi
    
    echo ""
    echo -e "${YELLOW}💡 To stop servers:${NC}"
    echo "   kill $API_PID $HTTP_PID"
    echo "   Or: pkill -f 'api_server|http.server'"
    echo ""
    echo -e "${YELLOW}💡 To monitor logs in realtime:${NC}"
    echo "   ./scripts/monitor_logs.sh"
    echo ""
    
    # Show recent logs
    echo -e "${BLUE}Recent API Server logs:${NC}"
    tail -n 5 /tmp/api_server.log 2>/dev/null || echo "   (No logs yet)"
    echo ""
    
    echo -e "${GREEN}✅ System ready!${NC}"
    echo ""
    echo "Press Ctrl+C to exit (servers will keep running in background)"
    
    # Wait for user interrupt
    trap "echo ''; echo 'Stopping...'; kill $API_PID $HTTP_PID 2>/dev/null; exit" INT TERM
    wait
else
    echo -e "${RED}❌ Failed to start servers${NC}"
    echo "Check logs:"
    echo "   tail /tmp/api_server.log"
    echo "   tail /tmp/dashboard_server.log"
    exit 1
fi

