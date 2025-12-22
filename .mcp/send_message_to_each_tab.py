#!/usr/bin/env python3
"""Gửi message đến từng tab agent để test - Switch tab trước khi gửi"""
import sys
import json
import time
import requests
from pathlib import Path
import importlib.util

PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"

# Import auto_submit_service để dùng switch_to_chat_tab
auto_submit_path = PROJECT_DIR / '.mcp' / 'auto_submit_service.py'
spec = importlib.util.spec_from_file_location('auto_submit_service', auto_submit_path)
auto_submit_service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auto_submit_service)

def send_to_each_tab(message: str = "Test message", delay_between: float = 1.5):
    """Gửi message đến từng tab agent - Switch tab trước khi gửi"""
    
    if not STATE_FILE.exists():
        print(f"❌ Không tìm thấy {STATE_FILE}")
        return False
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    detected_chats = state.get("detected_chats", [])
    if not detected_chats:
        print("⚠️  Không có chat nào đang mở trong session!")
        return False
    
    print(f"📤 Gửi message đến {len(detected_chats)} tabs (switch tab trước khi gửi)...")
    print("=" * 60)
    
    results = []
    
    for i, chat in enumerate(detected_chats):
        agent_name = chat.get('agent_name')
        chat_id = chat.get('chat_id') or chat.get('worktree_id')
        worktree_id = chat.get('worktree_id')
        model = chat.get('model', 'Unknown')
        
        if not agent_name:
            continue
        
        print(f"\n[{i+1}/{len(detected_chats)}] 🔄 Switch đến tab: {agent_name}")
        print(f"   Model: {model}")
        print(f"   Chat ID: {chat_id}")
        
        # BƯỚC 1: Focus vào đúng window của agent (Cursor dùng separate windows)
        print(f"   🔄 Đang focus vào window của {agent_name}...")
        window_status = auto_submit_service.find_and_focus_cursor_window(
            worktree_id=worktree_id,
            chat_id=chat_id,
            worktree_path=chat.get('worktree_path'),
            model=model
        )
        
        # Kiểm tra focus có thành công không
        if "focused" in window_status:
            print(f"   ✅ Đã focus vào window của {agent_name}")
        else:
            print(f"   ❌ Window focus failed: {window_status}")
            print(f"   ⏭️  Bỏ qua agent này (không gửi message)")
            results.append({'agent': agent_name, 'status': 'skipped_focus_failed'})
            if i < len(detected_chats) - 1:
                print(f"   ⏳ Đợi {delay_between}s trước khi focus tiếp...")
                time.sleep(delay_between)
            continue  # Bỏ qua agent này, không gửi message
        
        # Delay sau khi focus window
        time.sleep(0.5)
        
        # BƯỚC 2: Gửi message (chỉ khi switch thành công)
        print(f"   📨 Đang gửi message...")
        try:
            # Gửi qua API
            response = requests.post(
                'http://localhost:8001/api/messages',
                json={
                    'agent': agent_name,
                    'chat_id': chat_id,
                    'message': f"[{i+1}/{len(detected_chats)}] {message}",
                    'task_id': f'TEST_{i+1}',
                    'task_title': f'Test message to {agent_name}'
                },
                timeout=30
            )
            
            if response.ok:
                result = response.json()
                auto_submit = result.get('auto_submit', {})
                
                if auto_submit.get('success'):
                    print(f"   ✅ Đã gửi thành công!")
                    results.append({'agent': agent_name, 'status': 'success'})
                else:
                    msg = auto_submit.get('message', '')
                    print(f"   ⚠️  Gửi không thành công: {msg[:100]}")
                    results.append({'agent': agent_name, 'status': 'partial'})
            else:
                print(f"   ❌ API error: {response.status_code}")
                results.append({'agent': agent_name, 'status': 'error'})
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)[:100]}")
            results.append({'agent': agent_name, 'status': 'error'})
        
        # Delay giữa các messages
        if i < len(detected_chats) - 1:
            print(f"   ⏳ Đợi {delay_between}s trước khi switch tab tiếp...")
            time.sleep(delay_between)
    
    print("\n" + "=" * 60)
    print("📊 Kết quả:")
    success = sum(1 for r in results if r['status'] == 'success')
    print(f"   ✅ Thành công: {success}/{len(results)}")
    print(f"   ⚠️  Partial: {sum(1 for r in results if r['status'] == 'partial')}/{len(results)}")
    print(f"   ❌ Lỗi: {sum(1 for r in results if r['status'] == 'error')}/{len(results)}")
    
    return success == len(results)

if __name__ == "__main__":
    import sys
    
    message = sys.argv[1] if len(sys.argv) > 1 else "Test message từ script"
    delay = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
    
    print("🚀 Gửi message đến từng tab")
    print("=" * 60)
    print(f"Message: {message}")
    print(f"Delay: {delay}s giữa các tabs")
    print()
    
    success = send_to_each_tab(message, delay)
    sys.exit(0 if success else 1)

