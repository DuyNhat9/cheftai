#!/bin/bash
# Test multi-agent trigger: Tạo nhiều PENDING tasks cho nhiều agents
# Verify rằng monitor_service trigger tất cả agents đúng cách

cd "$(dirname "$0")/.."

echo "=== 🧪 TEST MULTI-AGENT TRIGGER ==="
echo ""
echo "Mục đích: Verify rằng monitor_service có thể trigger nhiều agents"
echo "          và focus đúng window cho từng agent"
echo ""

# Step 1: List các agents hiện có
echo "1️⃣ Checking available agents..."
python3 << 'PYTHON_SCRIPT'
import json
from pathlib import Path

state_file = Path('.mcp/shared_state.json')
with open(state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)

agents = state.get('agents', {})
print(f"   Found {len(agents)} agents:")
for agent_name, info in agents.items():
    model = info.get('model', 'Unknown')
    worktree_id = info.get('worktree_id', 'N/A')
    print(f"   - {agent_name}: {model} (worktree: {worktree_id})")
PYTHON_SCRIPT

echo ""
echo "2️⃣ Creating PENDING tasks for multiple agents..."
echo "   (This will test window focus logic for each agent)"
echo ""

# Step 2: Tạo PENDING tasks cho nhiều agents
python3 << 'PYTHON_SCRIPT'
import json
from pathlib import Path
from datetime import datetime

state_file = Path('.mcp/shared_state.json')
with open(state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)

agents = state.get('agents', {})
tasks = state.get('task_board', [])

# Tạo tasks cho các agents có worktree_id
test_tasks = []
for agent_name, info in agents.items():
    worktree_id = info.get('worktree_id')
    model = info.get('model', 'Unknown')
    if worktree_id:
        task_id = f"MULTI_TEST_{agent_name}_{int(datetime.now().timestamp())}"
        new_task = {
            "id": task_id,
            "title": f"Test Multi-Agent Trigger - {agent_name}",
            "owner": agent_name,
            "status": "PENDING",
            "description": f"Test message để verify window focus cho {agent_name} (model: {model}, worktree: {worktree_id}). Nếu bạn thấy message này trong Cursor chat thì auto-submit đang hoạt động đúng."
        }
        test_tasks.append(new_task)
        print(f"   ✅ Created task {task_id} for {agent_name}")

tasks.extend(test_tasks)
state['task_board'] = tasks

with open(state_file, 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print(f"\n   📋 Total {len(test_tasks)} PENDING tasks created")
PYTHON_SCRIPT

echo ""
echo "3️⃣ Monitor service should detect and trigger all agents..."
echo "   Check logs: tail -f /tmp/monitor_service.log"
echo ""

# Step 3: Đợi monitor service xử lý
sleep 8

echo "4️⃣ Checking monitor_service logs..."
if [ -f /tmp/monitor_service.log ]; then
    echo "   Recent activity:"
    tail -30 /tmp/monitor_service.log | grep -E "monitor_service|Triggering|Auto-submit|Waiting 5s" | tail -15
else
    echo "   ⚠️  No monitor_service.log found"
fi

echo ""
echo "5️⃣ Checking auto_submit debug logs..."
echo "   Look for window titles and focus status:"
tail -50 /tmp/monitor_service.log 2>/dev/null | grep -E "\[auto_submit_debug\]|DEBUG_" | tail -20 || echo "   (No debug logs found in monitor_service.log)"

echo ""
echo "=== ✅ TEST SUMMARY ==="
echo ""
echo "📋 Next Steps:"
echo "   1. Open Cursor and check each agent's chat window"
echo "   2. Verify messages appear in the correct chat for each agent"
echo "   3. Check window titles in debug logs to verify correct window focus"
echo ""
echo "💡 To monitor in real-time:"
echo "   tail -f /tmp/monitor_service.log | grep -E 'Triggering|DEBUG_|Waiting'"
echo ""
echo "💡 To check task status:"
echo "   python3 -c \"import json; f=open('.mcp/shared_state.json'); d=json.load(f); print('\\n'.join([f\"{t['id']}: {t['status']} (owner: {t['owner']})\" for t in d['task_board'] if 'MULTI_TEST' in t['id']]))\""



