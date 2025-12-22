#!/bin/bash
# Test full flow: Plan → Task PENDING → Monitor Service → Trigger Agent → Agent nhận message

cd "$(dirname "$0")/.."

echo "=== 🧪 TEST FULL FLOW END-TO-END ==="
echo ""

# Step 1: Tạo task PENDING trong shared_state.json
echo "1️⃣ Creating PENDING task for Architect..."
python3 << 'PYTHON_SCRIPT'
import json
from pathlib import Path
from datetime import datetime

state_file = Path('.mcp/shared_state.json')
with open(state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)

# Tạo task PENDING mới
task_id = f"TEST_FLOW_{int(datetime.now().timestamp())}"
new_task = {
    "id": task_id,
    "title": "Test Full Flow - Auto-submit message",
    "owner": "Architect",
    "status": "PENDING",
    "description": "Test message để verify flow end-to-end: Plan → Task → Monitor → Trigger → Agent nhận message trong Cursor chat"
}

tasks = state.get('task_board', [])
tasks.append(new_task)
state['task_board'] = tasks

with open(state_file, 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print(f"✅ Created task: {task_id}")
print(f"   Title: {new_task['title']}")
print(f"   Owner: {new_task['owner']}")
print(f"   Status: {new_task['status']}")
PYTHON_SCRIPT

echo ""
echo "2️⃣ Waiting for monitor_service to detect and trigger..."
echo "   (Monitor service should detect change in shared_state.json)"
echo "   (Check /tmp/monitor_service.log for details)"
echo ""

# Đợi monitor service xử lý
sleep 5

echo "3️⃣ Checking monitor_service logs..."
if [ -f /tmp/monitor_service.log ]; then
    echo "   Recent monitor_service activity:"
    tail -20 /tmp/monitor_service.log | grep -E "monitor_service|Triggering|Auto-submit" | tail -10
else
    echo "   ⚠️  No monitor_service.log found"
fi

echo ""
echo "4️⃣ Checking if prompt file was created..."
if [ -f .mcp/pending_prompts/Architect.md ]; then
    echo "   ✅ Prompt file exists: .mcp/pending_prompts/Architect.md"
    echo "   Content preview:"
    head -10 .mcp/pending_prompts/Architect.md | head -5
else
    echo "   ❌ Prompt file not found"
fi

echo ""
echo "5️⃣ Checking task status in shared_state.json..."
python3 << 'PYTHON_SCRIPT'
import json
from pathlib import Path

state_file = Path('.mcp/shared_state.json')
with open(state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)

tasks = state.get('task_board', [])
test_tasks = [t for t in tasks if t.get('id', '').startswith('TEST_FLOW_')]
if test_tasks:
    latest = sorted(test_tasks, key=lambda x: x.get('id', ''))[-1]
    print(f"   Task ID: {latest.get('id')}")
    print(f"   Status: {latest.get('status')}")
    if latest.get('status') == 'IN_PROGRESS':
        print("   ✅ Task status updated to IN_PROGRESS (monitor_service triggered successfully)")
    else:
        print("   ⚠️  Task status still PENDING (monitor_service may not have triggered)")
else:
    print("   ⚠️  No test tasks found")
PYTHON_SCRIPT

echo ""
echo "=== ✅ TEST SUMMARY ==="
echo ""
echo "📋 Next Steps:"
echo "   1. Open Cursor chat for Architect (worktree hng)"
echo "   2. Check if message appears in chat"
echo "   3. Verify message content matches task description"
echo ""
echo "💡 To check monitor_service status:"
echo "   tail -f /tmp/monitor_service.log"
echo ""
echo "💡 To manually trigger if needed:"
echo "   python3 .mcp/auto_submit_service.py Architect .mcp/pending_prompts/Architect.md hng 'Sonnet 4.5'"
