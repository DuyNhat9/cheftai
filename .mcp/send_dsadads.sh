#!/bin/bash
# Gửi "dsadads" cho tất cả agents

cd "$(dirname "$0")/.." || exit 1

echo "📤 Gửi message 'dsadads' cho các agents..."
echo "============================================================"

python3 << 'PYEOF'
import json
import subprocess
from pathlib import Path

PROJECT_DIR = Path.cwd()
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"
AUTO_SUBMIT_SCRIPT = PROJECT_DIR / ".mcp" / "auto_submit_service.py"

with open(STATE_FILE, 'r') as f:
    state = json.load(f)

detected_chats = state.get('detected_chats', [])
print(f'🔍 Tìm thấy {len(detected_chats)} agents:')
for chat in detected_chats:
    agent_name = chat.get('agent_name')
    chat_id = chat.get('worktree_id') or chat.get('chat_id')
    model = chat.get('model', 'Unknown')
    print(f'   - {agent_name:20} → {chat_id:5} ({model})')
print()

results = []
for chat in detected_chats:
    agent_name = chat.get('agent_name')
    chat_id = chat.get('worktree_id') or chat.get('chat_id')
    
    if not agent_name or not chat_id:
        continue
    
    try:
        cmd = ['python3', str(AUTO_SUBMIT_SCRIPT), agent_name, 'dsadads', chat_id]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20, cwd=str(PROJECT_DIR))
        
        if result.returncode == 0 and 'sent_to_cursor_ok' in result.stdout:
            print(f'✅ {agent_name:20} → {chat_id}: OK')
            results.append({'agent': agent_name, 'status': 'success'})
        else:
            output = result.stdout.strip() or result.stderr.strip() or 'Unknown error'
            print(f'⚠️  {agent_name:20} → {chat_id}: {output[:80]}')
            results.append({'agent': agent_name, 'status': 'partial'})
    except Exception as e:
        print(f'❌ {agent_name:20} → {chat_id}: {str(e)[:80]}')
        results.append({'agent': agent_name, 'status': 'error'})

print('============================================================')
success = sum(1 for r in results if r['status'] == 'success')
print(f'✅ Hoàn tất! Thành công: {success}/{len(results)}')
PYEOF

