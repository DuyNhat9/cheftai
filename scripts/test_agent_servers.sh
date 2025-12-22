#!/bin/bash
# Test script cho Agent Servers

echo "🧪 Testing Agent Servers"
echo "========================"
echo ""

BASE_URL="http://localhost:8001"

# Test 1: List agent servers
echo "1️⃣ Testing GET /api/agent-servers..."
response=$(curl -s "$BASE_URL/api/agent-servers")
if echo "$response" | python3 -m json.tool > /dev/null 2>&1; then
    echo "✅ GET /api/agent-servers: OK"
    echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'   Found {len(data)} agent servers')" 2>/dev/null
else
    echo "❌ GET /api/agent-servers: FAILED"
    echo "$response"
fi
echo ""

# Test 2: Health check for each agent server
echo "2️⃣ Testing health endpoints..."
for port in 8002 8003 8004 8005; do
    agent_name=""
    case $port in
        8002) agent_name="Architect" ;;
        8003) agent_name="Backend_AI_Dev" ;;
        8004) agent_name="UI_UX_Dev" ;;
        8005) agent_name="Testing_QA" ;;
    esac
    
    response=$(curl -s "http://localhost:$port/health" 2>/dev/null)
    if echo "$response" | python3 -m json.tool > /dev/null 2>&1; then
        status=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null)
        if [ "$status" = "healthy" ]; then
            echo "   ✅ $agent_name (port $port): Healthy"
        else
            echo "   ⚠️  $agent_name (port $port): Status = $status"
        fi
    else
        echo "   ❌ $agent_name (port $port): Not responding"
    fi
done
echo ""

# Test 3: Get status for each agent
echo "3️⃣ Testing GET /status endpoints..."
for port in 8002 8003 8004 8005; do
    agent_name=""
    case $port in
        8002) agent_name="Architect" ;;
        8003) agent_name="Backend_AI_Dev" ;;
        8004) agent_name="UI_UX_Dev" ;;
        8005) agent_name="Testing_QA" ;;
    esac
    
    response=$(curl -s "http://localhost:$port/status" 2>/dev/null)
    if echo "$response" | python3 -m json.tool > /dev/null 2>&1; then
        agent_status=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null)
        echo "   ✅ $agent_name: $agent_status"
    else
        echo "   ⚠️  $agent_name: Failed to get status"
    fi
done
echo ""

# Test 4: Get tasks for each agent
echo "4️⃣ Testing GET /tasks endpoints..."
for port in 8002 8003 8004 8005; do
    agent_name=""
    case $port in
        8002) agent_name="Architect" ;;
        8003) agent_name="Backend_AI_Dev" ;;
        8004) agent_name="UI_UX_Dev" ;;
        8005) agent_name="Testing_QA" ;;
    esac
    
    response=$(curl -s "http://localhost:$port/tasks" 2>/dev/null)
    if echo "$response" | python3 -m json.tool > /dev/null 2>&1; then
        task_count=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
        echo "   ✅ $agent_name: $task_count tasks"
    else
        echo "   ⚠️  $agent_name: Failed to get tasks"
    fi
done
echo ""

# Test 5: Test proxy endpoint
echo "5️⃣ Testing proxy endpoint..."
response=$(curl -s "$BASE_URL/api/agent/Architect/proxy/health" 2>/dev/null)
if echo "$response" | python3 -m json.tool > /dev/null 2>&1; then
    echo "✅ Proxy endpoint: OK"
    echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'   Agent: {data.get(\"agent\", \"unknown\")}')" 2>/dev/null
else
    echo "⚠️  Proxy endpoint: May not be working"
fi
echo ""

# Test 6: Test send_message endpoint (dry run)
echo "6️⃣ Testing POST /send_message (dry run)..."
for port in 8002 8003; do
    agent_name=""
    case $port in
        8002) agent_name="Architect" ;;
        8003) agent_name="Backend_AI_Dev" ;;
    esac
    
    response=$(curl -s -X POST "http://localhost:$port/send_message" \
        -H "Content-Type: application/json" \
        -d '{"message": "Test message from agent server API", "task_id": "TEST_MSG"}' 2>/dev/null)
    
    if echo "$response" | python3 -m json.tool > /dev/null 2>&1; then
        success=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)
        if [ "$success" = "True" ]; then
            echo "   ✅ $agent_name: Message sent successfully"
        else
            echo "   ⚠️  $agent_name: Message may have failed"
        fi
    else
        echo "   ⚠️  $agent_name: Failed to send message"
    fi
done
echo ""

echo "================================"
echo "✅ Agent servers test completed!"
echo ""
echo "💡 To test individual endpoints:"
echo "   curl http://localhost:8002/health"
echo "   curl http://localhost:8002/status"
echo "   curl http://localhost:8002/tasks"
echo ""

