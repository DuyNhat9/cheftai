#!/bin/bash
# Script tự động test và fix khi gửi message
# Usage: ./auto_test_and_fix.sh <agent> <message>

AGENT="$1"
MESSAGE="$2"

if [ -z "$AGENT" ] || [ -z "$MESSAGE" ]; then
    echo "Usage: $0 <agent> <message>"
    echo "Example: $0 Architect 'Test message'"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

echo "🔍 Auto Test & Fix - Testing message send..."

# Test 1: Kiểm tra API server đang chạy
echo ""
echo "1️⃣ Checking API server..."
if ! curl -s http://localhost:8001/api/state > /dev/null 2>&1; then
    echo "   ⚠️  API server không chạy, đang start..."
    pkill -f "api_server.py" 2>/dev/null
    python3 .mcp/api_server.py > /tmp/api_server.log 2>&1 &
    sleep 2
    if curl -s http://localhost:8001/api/state > /dev/null 2>&1; then
        echo "   ✅ API server đã được start"
    else
        echo "   ❌ Không thể start API server"
        exit 1
    fi
else
    echo "   ✅ API server đang chạy"
fi

# Test 2: Kiểm tra agent có trong shared_state không
echo ""
echo "2️⃣ Checking agent in shared_state..."
if [ -f ".mcp/shared_state.json" ]; then
    AGENT_EXISTS=$(python3 -c "import json; d=json.load(open('.mcp/shared_state.json')); print('$AGENT' in d.get('agents', {}))" 2>/dev/null)
    if [ "$AGENT_EXISTS" != "True" ]; then
        echo "   ⚠️  Agent '$AGENT' chưa có trong shared_state, đang scan worktrees..."
        python3 .mcp/detect_active_agents.py > /dev/null 2>&1
        echo "   ✅ Đã scan worktrees"
    else
        echo "   ✅ Agent '$AGENT' có trong shared_state"
    fi
else
    echo "   ⚠️  shared_state.json không tồn tại, đang tạo..."
    python3 .mcp/detect_active_agents.py > /dev/null 2>&1
    echo "   ✅ Đã tạo shared_state.json"
fi

# Test 3: Gửi message với retry
echo ""
echo "3️⃣ Sending message..."
MAX_RETRIES=3
RETRY_COUNT=0
SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$SUCCESS" = false ]; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Attempt $RETRY_COUNT/$MAX_RETRIES..."
    
    RESPONSE=$(python3 .mcp/send_message.py "$AGENT" "$MESSAGE" 2>&1)
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        SUCCESS=true
        echo "   ✅ Message sent successfully!"
        echo "$RESPONSE"
    else
        echo "   ⚠️  Attempt $RETRY_COUNT failed"
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "   🔄 Retrying in 2 seconds..."
            sleep 2
        else
            echo "   ❌ All attempts failed"
            echo "$RESPONSE"
            exit 1
        fi
    fi
done

# Test 4: Verify message was sent
echo ""
echo "4️⃣ Verifying message..."
sleep 1
if [ -f ".mcp/pending_prompts/${AGENT}.md" ]; then
    echo "   ✅ Prompt file created: .mcp/pending_prompts/${AGENT}.md"
    FILE_SIZE=$(stat -f%z ".mcp/pending_prompts/${AGENT}.md" 2>/dev/null || stat -c%s ".mcp/pending_prompts/${AGENT}.md" 2>/dev/null)
    if [ "$FILE_SIZE" -gt 0 ]; then
        echo "   ✅ File size: ${FILE_SIZE} bytes"
    else
        echo "   ⚠️  File is empty"
    fi
else
    echo "   ⚠️  Prompt file not found"
fi

echo ""
echo "✅ Auto Test & Fix completed!"

