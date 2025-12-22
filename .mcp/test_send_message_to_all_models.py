#!/usr/bin/env python3
"""Test gửi tin nhắn 'dsadads' cho từng model qua API"""
import requests
import json
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"

def test_send_to_all_models(message: str = "dsadads"):
    """Gửi message đến tất cả models qua API"""
    
    print(f"📤 Testing gửi message '{message}' cho từng model qua API")
    print("=" * 60)
    
    # Load detected_chats để lấy danh sách agents
    if not STATE_FILE.exists():
        print(f"❌ Không tìm thấy {STATE_FILE}")
        return
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    detected_chats = state.get("detected_chats", [])
    
    if not detected_chats:
        print("⚠️  Không có agents nào trong detected_chats")
        return
    
    print(f"📋 Tìm thấy {len(detected_chats)} agents:")
    for i, chat in enumerate(detected_chats):
        print(f"   [{i+1}] {chat.get('agent_name')}: {chat.get('model')}")
    
    print("\n" + "=" * 60)
    print("🚀 Bắt đầu gửi messages...")
    print("=" * 60)
    
    results = []
    
    for i, chat in enumerate(detected_chats):
        agent_name = chat.get('agent_name')
        chat_id = chat.get('chat_id') or chat.get('worktree_id')
        model = chat.get('model', 'Unknown')
        
        if not agent_name:
            continue
        
        print(f"\n[{i+1}/{len(detected_chats)}] 📨 Gửi đến: {agent_name}")
        print(f"   Model: {model}")
        print(f"   Chat ID: {chat_id}")
        
        try:
            # Gửi qua API /api/messages
            response = requests.post(
                'http://localhost:8001/api/messages',
                json={
                    'agent': agent_name,
                    'chat_id': chat_id,
                    'message': message,
                    'task_id': f'TEST_{i+1}',
                    'task_title': f'Test message: {message}'
                },
                timeout=30
            )
            
            if response.ok:
                result = response.json()
                auto_submit = result.get('auto_submit', {})
                
                if auto_submit.get('success'):
                    print(f"   ✅ Gửi thành công!")
                    results.append({
                        'agent': agent_name,
                        'model': model,
                        'status': 'success'
                    })
                else:
                    msg = auto_submit.get('message', '')
                    print(f"   ⚠️  Gửi không thành công: {msg[:100]}")
                    results.append({
                        'agent': agent_name,
                        'model': model,
                        'status': 'partial',
                        'error': msg[:100]
                    })
            else:
                print(f"   ❌ API error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown')}")
                except:
                    print(f"   Error: {response.text[:100]}")
                results.append({
                    'agent': agent_name,
                    'model': model,
                    'status': 'error',
                    'error': f"HTTP {response.status_code}"
                })
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Không kết nối được API server")
            results.append({
                'agent': agent_name,
                'model': model,
                'status': 'error',
                'error': 'ConnectionError'
            })
        except Exception as e:
            print(f"   ❌ Exception: {str(e)[:100]}")
            results.append({
                'agent': agent_name,
                'model': model,
                'status': 'error',
                'error': str(e)[:100]
            })
        
        # Delay giữa các messages
        if i < len(detected_chats) - 1:
            print(f"   ⏳ Đợi 2s trước khi gửi tiếp...")
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("📊 Kết quả:")
    success = sum(1 for r in results if r['status'] == 'success')
    partial = sum(1 for r in results if r['status'] == 'partial')
    errors = sum(1 for r in results if r['status'] == 'error')
    
    print(f"   ✅ Thành công: {success}/{len(results)}")
    print(f"   ⚠️  Partial: {partial}/{len(results)}")
    print(f"   ❌ Lỗi: {errors}/{len(results)}")
    
    print("\n📋 Chi tiết:")
    for r in results:
        status_icon = "✅" if r['status'] == 'success' else "⚠️" if r['status'] == 'partial' else "❌"
        print(f"   {status_icon} {r['agent']:20} ({r['model']:30}) - {r['status']}")
        if 'error' in r:
            print(f"      Error: {r['error']}")
    
    return success == len(results)

if __name__ == "__main__":
    import sys
    
    message = sys.argv[1] if len(sys.argv) > 1 else "dsadads"
    
    print("🧪 Test Gửi Message Qua API")
    print("=" * 60)
    print(f"Message: {message}")
    print()
    
    success = test_send_to_all_models(message)
    sys.exit(0 if success else 1)

