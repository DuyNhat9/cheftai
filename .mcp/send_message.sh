#!/bin/bash
# Script để gửi message từ terminal thông qua API
# Usage: ./send_message.sh <agent> <message>
# Example: ./send_message.sh Architect "Hello from terminal"

API_URL="http://localhost:8001/api/messages"
AGENT="$1"
MESSAGE="$2"

if [ -z "$AGENT" ] || [ -z "$MESSAGE" ]; then
    echo "Usage: $0 <agent> <message>"
    echo "Example: $0 Architect 'Hello from terminal'"
    exit 1
fi

# Gửi message qua API
RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{
        \"agent\": \"$AGENT\",
        \"message\": \"$MESSAGE\",
        \"task_id\": \"ADHOC\",
        \"task_title\": \"Message from terminal\"
    }")

# Parse và hiển thị kết quả
SUCCESS=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null)
TRIGGER_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('trigger_id', 'N/A'))" 2>/dev/null)
AUTO_SUBMIT=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('auto_submit', {}).get('success', False))" 2>/dev/null)

if [ "$SUCCESS" = "True" ]; then
    echo "✅ Message sent successfully!"
    echo "   Trigger ID: $TRIGGER_ID"
    if [ "$AUTO_SUBMIT" = "True" ]; then
        echo "   ✅ Auto-submitted to Cursor chat"
    else
        echo "   ⚠️  Auto-submit skipped or failed"
    fi
    echo ""
    echo "Full response:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
else
    echo "❌ Failed to send message"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    exit 1
fi

