#!/bin/bash
# Script test flow trigger → agent working → sync

echo "🧪 Testing Backend Trigger Flow"
echo "================================"
echo ""

BASE_URL="http://localhost:8001"

# Test 1: Trigger một agent
echo "1️⃣ Testing POST /api/messages (trigger agent)..."
response=$(curl -s -X POST "$BASE_URL/api/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "Backend_AI_Dev",
    "message": "Test trigger - hãy làm task B200",
    "task_id": "B200",
    "task_title": "Backend: Rà soát API /api/messages và /api/auto-submit"
  }')

echo "$response" | python3 -m json.tool > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ POST /api/messages: OK"
    trigger_id=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('trigger_id', 'N/A'))" 2>/dev/null)
    echo "   📊 Trigger ID: $trigger_id"
else
    echo "❌ POST /api/messages: FAILED"
    exit 1
fi
echo ""

# Test 2: Update task status → IN_PROGRESS
echo "2️⃣ Testing POST /api/update-task (set IN_PROGRESS)..."
response=$(curl -s -X POST "$BASE_URL/api/update-task" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "B200",
    "status": "IN_PROGRESS",
    "owner": "Backend_AI_Dev",
    "title": "Backend: Rà soát API /api/messages và /api/auto-submit"
  }')

echo "$response" | python3 -m json.tool > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ POST /api/update-task: OK"
    success=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)
    echo "   📊 Success: $success"
else
    echo "❌ POST /api/update-task: FAILED"
    exit 1
fi
echo ""

# Test 3: Check agent status sau khi update task
echo "3️⃣ Checking agent status after task update..."
sleep 1
state_response=$(curl -s "$BASE_URL/api/state")
backend_status=$(echo "$state_response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('agents',{}).get('Backend_AI_Dev',{}).get('status','Unknown'))" 2>/dev/null)
b200_status=$(echo "$state_response" | python3 -c "import sys, json; data=json.load(sys.stdin); tasks=data.get('task_board',[]); print([t.get('status') for t in tasks if t.get('id')=='B200'][0] if [t for t in tasks if t.get('id')=='B200'] else 'Not found')" 2>/dev/null)

echo "   📊 Backend_AI_Dev status: $backend_status"
echo "   📊 B200 task status: $b200_status"

if [ "$b200_status" = "IN_PROGRESS" ]; then
    echo "   ✅ Task status updated correctly"
else
    echo "   ⚠️  Task status may not be updated"
fi

# Note: Agent status sẽ là Idle nếu chat không active (>30 phút hoặc không có chat info)
if [ "$backend_status" = "Working" ]; then
    echo "   ✅ Agent status synced to Working (chat is active)"
elif [ "$backend_status" = "Idle" ]; then
    echo "   ℹ️  Agent status is Idle (chat not active or no chat info)"
else
    echo "   ⚠️  Unexpected agent status: $backend_status"
fi
echo ""

# Test 4: Simulate chat active (update detected_chats)
echo "4️⃣ Testing with simulated active chat..."
# Tạo một test script Python để update chat activity
python3 << 'PYTHON_SCRIPT'
import json
from pathlib import Path
from datetime import datetime, timedelta

state_file = Path('.mcp/shared_state.json')
with open(state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)

# Update detected_chats để simulate chat active
detected_chats = state.get('detected_chats', [])
for chat in detected_chats:
    if chat.get('agent_name') == 'Backend_AI_Dev':
        # Set chat active (1 phút trước)
        chat['modified_minutes_ago'] = 1.0
        chat['last_active'] = (datetime.now() - timedelta(minutes=1)).isoformat()
        print(f"✅ Updated chat activity for Backend_AI_Dev: {chat.get('modified_minutes_ago')} min ago")

# Save
with open(state_file, 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
PYTHON_SCRIPT

if [ $? -eq 0 ]; then
    echo "   ✅ Chat activity updated"
else
    echo "   ⚠️  Failed to update chat activity"
fi
echo ""

# Test 5: Check agent status sau khi chat active
echo "5️⃣ Checking agent status after chat becomes active..."
sleep 1
state_response=$(curl -s "$BASE_URL/api/state")
backend_status=$(echo "$state_response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('agents',{}).get('Backend_AI_Dev',{}).get('status','Unknown'))" 2>/dev/null)
backend_task=$(echo "$state_response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('agents',{}).get('Backend_AI_Dev',{}).get('current_task','None'))" 2>/dev/null)

echo "   📊 Backend_AI_Dev status: $backend_status"
echo "   📊 Backend_AI_Dev current_task: $backend_task"

if [ "$backend_status" = "Working" ]; then
    echo "   ✅ Agent status synced to Working (chat active + task IN_PROGRESS)"
elif [ "$backend_status" = "Idle" ]; then
    echo "   ⚠️  Agent status is still Idle (may need to check sync logic)"
else
    echo "   ⚠️  Unexpected agent status: $backend_status"
fi
echo ""

# Test 6: Test multiple agents
echo "6️⃣ Testing multiple agents trigger..."
agents=("UI_UX_Dev" "Testing_QA")
for agent in "${agents[@]}"; do
    echo "   Testing $agent..."
    response=$(curl -s -X POST "$BASE_URL/api/messages" \
      -H "Content-Type: application/json" \
      -d "{
        \"agent\": \"$agent\",
        \"message\": \"Test trigger for $agent\",
        \"task_id\": \"TEMP_$(date +%s)\",
        \"task_title\": \"Test task for $agent\"
      }")
    
    success=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)
    if [ "$success" = "True" ]; then
        echo "   ✅ $agent: Trigger created"
    else
        echo "   ⚠️  $agent: Trigger may have failed"
    fi
done
echo ""

echo "================================"
echo "✅ Backend trigger flow test completed!"
echo ""
echo "💡 Summary:"
echo "   - POST /api/messages: Creates trigger and prompt file"
echo "   - POST /api/update-task: Updates task status"
echo "   - GET /api/state: Auto-syncs agent status based on:"
echo "     * Task status (IN_PROGRESS)"
echo "     * Chat activity (<30 min = active)"
echo ""

