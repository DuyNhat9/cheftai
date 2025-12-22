#!/usr/bin/env python3
"""Test simplified logic after restart"""
import requests
import json

print('📤 Testing với API server mới')
print('=' * 60)

try:
    response = requests.post(
        'http://localhost:8001/api/messages',
        json={
            'agent': 'Architect',
            'chat_id': 'qnu',
            'message': 'Test sau khi restart API server',
            'task_id': 'TEST',
            'task_title': 'Test After Restart'
        },
        timeout=30
    )
    
    if response.ok:
        result = response.json()
        print('✅ Status: Success')
        auto_submit = result.get('auto_submit', {})
        print('📋 Auto-submit success:', auto_submit.get('success'))
        
        msg = auto_submit.get('message', '')
        
        # Check for key messages
        if 'tiếp tục gửi message' in msg:
            print('✅ Đã thấy log: "tiếp tục gửi message"')
        if 'sent_to_cursor_ok' in msg:
            print('✅ Message đã được gửi thành công!')
        if 'Aborting message send' in msg:
            print('❌ VẪN CÒN ABORT LOGIC!')
        
        # Show relevant log snippet
        lines = msg.split('\n')
        for line in lines:
            if 'tiếp tục' in line or 'Aborting' in line or 'sent_to_cursor' in line:
                print(f'📝 {line}')
    else:
        print('❌ Error:', response.status_code)
        
except Exception as e:
    print(f'❌ Exception: {e}')

