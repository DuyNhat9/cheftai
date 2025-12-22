#!/bin/bash
# Script để test backend API server

echo "🧪 Testing Backend API Server"
echo "=============================="
echo ""

BASE_URL="http://localhost:8001"

# Test 1: GET /api/state
echo "1️⃣ Testing GET /api/state (with auto-sync)..."
response=$(curl -s "$BASE_URL/api/state")
if [ $? -eq 0 ]; then
    echo "✅ GET /api/state: OK"
    # Check if response is valid JSON
    echo "$response" | python3 -m json.tool > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "   ✅ Response is valid JSON"
        # Check agent status sync
        agents_working=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len([a for a in data.get('agents',{}).values() if a.get('status')=='Working']))" 2>/dev/null)
        tasks_in_progress=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len([t for t in data.get('task_board',[]) if t.get('status')=='IN_PROGRESS']))" 2>/dev/null)
        echo "   📊 Agents Working: $agents_working"
        echo "   📊 Tasks IN_PROGRESS: $tasks_in_progress"
        
        if [ "$agents_working" -eq "$tasks_in_progress" ]; then
            echo "   ✅ Agent status synced with tasks!"
        else
            echo "   ⚠️  Agent status may not be synced (Working agents != IN_PROGRESS tasks)"
        fi
    else
        echo "   ❌ Response is not valid JSON"
    fi
else
    echo "❌ GET /api/state: FAILED"
fi
echo ""

# Test 2: GET /api/agents
echo "2️⃣ Testing GET /api/agents..."
response=$(curl -s "$BASE_URL/api/agents")
if [ $? -eq 0 ]; then
    echo "$response" | python3 -m json.tool > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ GET /api/agents: OK (valid JSON)"
    else
        echo "❌ GET /api/agents: Invalid JSON"
    fi
else
    echo "❌ GET /api/agents: FAILED"
fi
echo ""

# Test 3: GET /api/task_board
echo "3️⃣ Testing GET /api/task_board..."
response=$(curl -s "$BASE_URL/api/task_board")
if [ $? -eq 0 ]; then
    echo "$response" | python3 -m json.tool > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ GET /api/task_board: OK (valid JSON)"
    else
        echo "❌ GET /api/task_board: Invalid JSON"
    fi
else
    echo "❌ GET /api/task_board: FAILED"
fi
echo ""

# Test 4: POST /api/update-task (test sync)
echo "4️⃣ Testing POST /api/update-task (sync test)..."
# Create a test task update
test_data='{"task_id":"A200","status":"COMPLETED","owner":"Architect"}'
response=$(curl -s -X POST "$BASE_URL/api/update-task" \
    -H "Content-Type: application/json" \
    -d "$test_data")
if [ $? -eq 0 ]; then
    echo "$response" | python3 -m json.tool > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ POST /api/update-task: OK"
        # Check if Architect status was synced
        sleep 1
        state_response=$(curl -s "$BASE_URL/api/state")
        architect_status=$(echo "$state_response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('agents',{}).get('Architect',{}).get('status','Unknown'))" 2>/dev/null)
        echo "   📊 Architect status after update: $architect_status"
        if [ "$architect_status" = "Idle" ]; then
            echo "   ✅ Agent status auto-synced correctly!"
        else
            echo "   ⚠️  Agent status may not be synced"
        fi
        # Restore task
        restore_data='{"task_id":"A200","status":"IN_PROGRESS","owner":"Architect","title":"Architect: Kiểm tra lại flow Start → Trigger → Auto-submit"}'
        curl -s -X POST "$BASE_URL/api/update-task" \
            -H "Content-Type: application/json" \
            -d "$restore_data" > /dev/null
        echo "   🔄 Restored A200 to IN_PROGRESS"
    else
        echo "❌ POST /api/update-task: Invalid JSON response"
    fi
else
    echo "❌ POST /api/update-task: FAILED"
fi
echo ""

# Test 5: Check API server logs
echo "5️⃣ Checking API server logs..."
if [ -f "/tmp/api_server.log" ]; then
    echo "✅ Log file exists: /tmp/api_server.log"
    sync_logs=$(grep -c "Auto-sync" /tmp/api_server.log 2>/dev/null || echo "0")
    sync_logs=${sync_logs:-0}
    echo "   📊 Auto-sync log entries: $sync_logs"
    if [ "$sync_logs" -gt 0 ]; then
        echo "   ✅ Sync logging is working"
    fi
else
    echo "⚠️  Log file not found: /tmp/api_server.log"
fi
echo ""

echo "=============================="
echo "✅ Backend test completed!"
echo ""
echo "💡 To monitor logs in real-time:"
echo "   tail -f /tmp/api_server.log"
echo ""

