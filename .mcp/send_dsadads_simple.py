#!/usr/bin/env python3
"""Simple script to send a message to all agents via API"""
import requests
import json
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"
API_URL = "http://localhost:8001/api/messages"

def send_to_all_agents(message: str = "dsadads"):
    """Send message to all agents via API"""
    
    print(f"📤 Gửi '{message}' cho từng agent...")
    print("=" * 60)
    
    # Load detected_chats
    if not STATE_FILE.exists():
        print(f"❌ Không tìm thấy {STATE_FILE}")
        return
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    detected_chats = state.get("detected_chats", [])
    
    if not detected_chats:
        print("⚠️  Không có agents nào trong detected_chats")
        return
    
    print(f"Tìm thấy {len(detected_chats)} agents:")
    for i, chat in enumerate(detected_chats):
        agent_name = chat.get('agent_name', 'Unknown')
        model = chat.get('model', 'Unknown')
        print(f"[{i+1}/{len(detected_chats)}] {agent_name:20} ({model})")
    
    print("=" * 60)
    
    # Send to each agent
    for i, chat in enumerate(detected_chats):
        agent_name = chat.get('agent_name')
        chat_id = chat.get('chat_id') or chat.get('worktree_id')
        model = chat.get('model', 'Unknown')
        
        if not agent_name:
            continue
        
        print(f"\n[{i+1}/{len(detected_chats)}] 📨 {agent_name} ({model})")
        
        try:
            response = requests.post(
                API_URL,
                json={
                    'agent': agent_name,
                    'chat_id': chat_id,
                    'message': message,
                    'task_id': 'TEST',
                    'task_title': f'Test: {message}'
                },
                timeout=15  # Tăng timeout để đợi auto_submit_service hoàn tất
            )
            
            if response.ok:
                result = response.json()
                auto_submit = result.get('auto_submit', {})
                if auto_submit.get('success'):
                    print(f"  ✅ Thành công")
                else:
                    print(f"  ⚠️  {auto_submit.get('message', 'Failed')[:50]}")
            else:
                print(f"  ❌ HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Không kết nối được API server (port 8001)")
        except requests.exceptions.Timeout:
            print(f"  ❌ Timeout")
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:50]}")
        
        if i < len(detected_chats) - 1:
            time.sleep(1)
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    import sys
    message = sys.argv[1] if len(sys.argv) > 1 else "dsadads"
    send_to_all_agents(message)
