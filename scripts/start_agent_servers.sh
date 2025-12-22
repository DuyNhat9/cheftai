#!/bin/bash
# Script để start tất cả agent servers

echo "🚀 Starting Agent Servers..."
echo "============================"
echo ""

cd "$(dirname "$0")/.."

# Load config + shared state (để lấy model realtime)
CONFIG_FILE=".mcp/agent_servers_config.json"
SHARED_STATE_FILE=".mcp/shared_state.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config file not found: $CONFIG_FILE"
    exit 1
fi
if [ ! -f "$SHARED_STATE_FILE" ]; then
    echo "❌ Shared state not found: $SHARED_STATE_FILE"
    exit 1
fi

# Kill existing agent servers
echo "🧹 Cleaning up existing agent servers..."
pkill -f "architect_server.py" 2>/dev/null || true
pkill -f "backend_server.py" 2>/dev/null || true
pkill -f "ui_server.py" 2>/dev/null || true
pkill -f "qa_server.py" 2>/dev/null || true
pkill -f "supervisor_server.py" 2>/dev/null || true
pkill -f "gemini_server.py" 2>/dev/null || true
sleep 1

# Start each agent server
PIDS=()
AGENTS=()

while IFS= read -r line; do
    # Extract agent name and port from config (simple parsing)
    if [[ $line =~ \"([^\"]+)\".*\"port\":\ *([0-9]+) ]]; then
        AGENT_NAME="${BASH_REMATCH[1]}"
        PORT="${BASH_REMATCH[2]}"
        
        # Lấy model realtime từ shared_state.json
        MODEL=$(python3 - <<PY
import json
agent="$AGENT_NAME"
state=json.load(open("$SHARED_STATE_FILE", "r", encoding="utf-8"))
info=state.get("agents", {}).get(agent, {})
print(info.get("model", "Unknown"))
PY
)

        # Map agent name to server file
        case "$AGENT_NAME" in
            "Architect")
                SERVER_FILE=".mcp/agents/architect_server.py"
                ;;
            "Backend_AI_Dev")
                SERVER_FILE=".mcp/agents/backend_server.py"
                ;;
            "UI_UX_Dev")
                SERVER_FILE=".mcp/agents/ui_server.py"
                ;;
            "Testing_QA")
                SERVER_FILE=".mcp/agents/qa_server.py"
                ;;
            "Supervisor")
                SERVER_FILE=".mcp/agents/supervisor_server.py"
                ;;
            "Gemini_3_Pro")
                SERVER_FILE=".mcp/agents/gemini_server.py"
                ;;
            *)
                echo "⚠️  Unknown agent: $AGENT_NAME, skipping"
                continue
                ;;
        esac
        
        # Check if port is available
        if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
            echo "⚠️  Port $PORT already in use for $AGENT_NAME, skipping"
            continue
        fi
        
        # Start server
        echo "📡 Starting $AGENT_NAME [$MODEL] on port $PORT..."
        python3 "$SERVER_FILE" > "/tmp/agent_${AGENT_NAME}.log" 2>&1 &
        PID=$!
        PIDS+=($PID)
        AGENTS+=("$AGENT_NAME:$PORT:$MODEL")
        
        sleep 1
        
        # Check if started successfully
        if ps -p $PID > /dev/null 2>&1; then
            echo "   ✅ Started (PID: $PID)"
        else
            echo "   ❌ Failed to start"
            tail -5 "/tmp/agent_${AGENT_NAME}.log"
        fi
    fi
done < <(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); [print(f'{k}:{v[\"port\"]}') for k,v in config.items()]")

sleep 2

# Verify all servers
echo ""
echo "🔍 Verifying servers..."
ALL_OK=true
for agent_port in "${AGENTS[@]}"; do
    IFS=':' read -r AGENT_NAME PORT MODEL <<< "$agent_port"
    if curl -s "http://localhost:$PORT/health" > /dev/null 2>&1; then
        echo "   ✅ $AGENT_NAME [$MODEL] (port $PORT): Healthy"
    else
        echo "   ❌ $AGENT_NAME [$MODEL] (port $PORT): Not responding"
        ALL_OK=false
    fi
done

if [ "$ALL_OK" = true ]; then
    echo ""
    echo "✅ All agent servers started!"
    echo ""
    echo "📊 Agent Server URLs:"
    for agent_port in "${AGENTS[@]}"; do
        IFS=':' read -r AGENT_NAME PORT MODEL <<< "$agent_port"
        echo "   - $AGENT_NAME [$MODEL]: http://localhost:$PORT"
    done
    echo ""
    echo "📝 Log Files:"
    for agent_port in "${AGENTS[@]}"; do
        IFS=':' read -r AGENT_NAME PORT MODEL <<< "$agent_port"
        echo "   - $AGENT_NAME: /tmp/agent_${AGENT_NAME}.log"
    done
    echo ""
    echo "💡 To stop all servers:"
    echo "   pkill -f 'architect_server|backend_server|ui_server|qa_server|supervisor_server|gemini_server'"
    echo "   Or: kill ${PIDS[*]}"
else
    echo ""
    echo "⚠️  Some servers failed to start. Check logs above."
    exit 1
fi

