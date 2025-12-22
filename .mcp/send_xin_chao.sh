#!/bin/bash
# Gửi "xin chào em yêu" cho tất cả agents

cd "$(dirname "$0")/.." || exit 1

echo "📤 Gửi 'xin chào em yêu' cho tất cả agents..."
echo "============================================================"

python3 << 'PYEOF'
import json
import requests
import time
from pathlib import Path

PROJECT_DIR = Path.cwd()
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"
API_URL = "http://localhost:8001/api/messages"

with open(STATE_FILE, 'r') as f:
    state = json.load(f)

detected_chats = state.get('detected_chats', [])
print(f'Tìm thấy {len(detected_chats)} agents:\n')

for i, chat in enumerate(detected_chats, 1):
    agent_name = chat.get('agent_name')
    chat_id = chat.get('worktree_id') or chat.get('chat_id')
    model = chat.get('model', 'Unknown')
    
    if not agent_name:
        continue
    
    print(f'[{i}/{len(detected_chats)}] 📨 {agent_name:20} ({model})')
    
    try:
        response = requests.post(
            API_URL,
            json={
                'agent': agent_name,
                'chat_id': chat_id,
                'message': 'xin chào em yêu',
                'task_id': 'TEST',
                'task_title': 'Test: xin chào em yêu'
            },
            timeout=15
        )
        
        if response.ok:
            result = response.json()
            auto_submit = result.get('auto_submit', {})
            if auto_submit.get('success'):
                print(f'  ✅ Thành công\n')
            else:
                msg = auto_submit.get('message', 'Failed')[:60]
                print(f'  ⚠️  {msg}\n')
        else:
            print(f'  ❌ HTTP {response.status_code}\n')
    except Exception as e:
        print(f'  ❌ Error: {str(e)[:60]}\n')
    
    if i < len(detected_chats):
        time.sleep(1)

print('============================================================')
print('✅ Hoàn tất!')
PYEOF

