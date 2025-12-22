#!/bin/bash
# Real-time log monitor cho CheftAi Multi-Agent System
# Usage: ./scripts/monitor_logs.sh [options]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MCP_DIR="$PROJECT_DIR/.mcp"

cd "$PROJECT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🍳 CheftAi Multi-Agent System - Log Monitor${NC}"
echo -e "${BLUE}===========================================${NC}\n"

# Check if log_monitor.py exists
if [ ! -f "$MCP_DIR/log_monitor.py" ]; then
    echo -e "${RED}❌ log_monitor.py not found!${NC}"
    exit 1
fi

# Parse arguments
SERVICE="all"
FILTER=""
ERROR_ONLY=false
API_ONLY=false
TRIGGER_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--service)
            SERVICE="$2"
            shift 2
            ;;
        -f|--filter)
            FILTER="$2"
            shift 2
            ;;
        --error-only)
            ERROR_ONLY=true
            shift
            ;;
        --api-only)
            API_ONLY=true
            shift
            ;;
        --trigger-only)
            TRIGGER_ONLY=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -s, --service SERVICE    Monitor specific service (api, dashboard, auto_submit, general, all)"
            echo "  -f, --filter PATTERN    Filter logs by regex pattern"
            echo "  --error-only            Show only errors"
            echo "  --api-only              Show only API-related logs"
            echo "  --trigger-only          Show only trigger/agent-related logs"
            echo "  -h, --help              Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                      # Monitor all logs"
            echo "  $0 -s api               # Monitor only API server logs"
            echo "  $0 --error-only         # Show only errors"
            echo "  $0 -f 'trigger'         # Filter by 'trigger'"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Build command
CMD="python3 $MCP_DIR/log_monitor.py"

if [ "$SERVICE" != "all" ]; then
    CMD="$CMD -s $SERVICE"
fi

if [ -n "$FILTER" ]; then
    CMD="$CMD -f '$FILTER'"
fi

if [ "$ERROR_ONLY" = true ]; then
    CMD="$CMD --error-only"
fi

if [ "$API_ONLY" = true ]; then
    CMD="$CMD --api-only"
fi

if [ "$TRIGGER_ONLY" = true ]; then
    CMD="$CMD --trigger-only"
fi

# Check log files
echo -e "${YELLOW}Checking log files...${NC}"
LOG_FILES=(
    "/tmp/api_server.log"
    "/tmp/dashboard_server.log"
    "/tmp/auto_submit.log"
    "/tmp/cheftai.log"
)

MISSING_FILES=()
for log_file in "${LOG_FILES[@]}"; do
    if [ ! -f "$log_file" ]; then
        MISSING_FILES+=("$log_file")
    else
        SIZE=$(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file" 2>/dev/null || echo "0")
        if [ "$SIZE" -gt 0 ]; then
            echo -e "${GREEN}✅${NC} $log_file ($(numfmt --to=iec-i --suffix=B $SIZE 2>/dev/null || echo "${SIZE}B"))"
        else
            echo -e "${YELLOW}⚠️${NC}  $log_file (empty)"
        fi
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Missing log files (will be created when services start):${NC}"
    for file in "${MISSING_FILES[@]}"; do
        echo "   - $file"
    done
    echo ""
    echo -e "${BLUE}💡 Start services to generate logs:${NC}"
    echo "   python3 .mcp/api_server.py > /tmp/api_server.log 2>&1 &"
    echo "   python3 .mcp/dashboard_server.py > /tmp/dashboard_server.log 2>&1 &"
    echo ""
fi

echo ""
echo -e "${GREEN}Starting log monitor...${NC}"
echo -e "${BLUE}Command: $CMD${NC}\n"

# Run monitor
eval $CMD

