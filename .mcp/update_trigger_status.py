#!/usr/bin/env python3
"""Update trigger status in trigger_queue.json"""

import json
from pathlib import Path
from datetime import datetime

trigger_file = Path('.mcp/trigger_queue.json')
if trigger_file.exists():
    with open(trigger_file, 'r', encoding='utf-8') as f:
        triggers = json.load(f)
    
    # Tìm trigger mới nhất cho chat_id này
    chat_id = 'ff348693-5a66-4c61-b8ca-69ff99780e6e'
    latest_trigger = None
    for trigger in reversed(triggers.get('triggers', [])):
        if trigger.get('chat_id') == chat_id and trigger.get('status') == 'pending':
            latest_trigger = trigger
            break
    
    if latest_trigger:
        print('✅ Tìm thấy trigger mới nhất:')
        print(f'  ID: {latest_trigger.get("id")}')
        print(f'  Status: {latest_trigger.get("status")}')
        print(f'  Agent: {latest_trigger.get("agent")}')
        print(f'  Task: {latest_trigger.get("task_title")}')
        
        # Cập nhật status thành 'processing'
        latest_trigger['status'] = 'processing'
        latest_trigger['processed_at'] = datetime.utcnow().isoformat() + 'Z'
        
        with open(trigger_file, 'w', encoding='utf-8') as f:
            json.dump(triggers, f, indent=2, ensure_ascii=False)
        
        print('\n✅ Đã cập nhật trigger status thành "processing"')
    else:
        print('❌ Không tìm thấy trigger pending cho chat_id này')


