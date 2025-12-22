#!/usr/bin/env python3
"""
Test tính năng chuyển tab giữa các model trong Cursor
"""
import sys
import json
from pathlib import Path

# Add parent directory to path để import auto_submit_service
PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))

# Import trực tiếp từ file
import importlib.util
spec = importlib.util.spec_from_file_location("auto_submit_service", PROJECT_DIR / ".mcp" / "auto_submit_service.py")
auto_submit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auto_submit)

switch_to_chat_tab = auto_submit.switch_to_chat_tab
get_agent_worktree_info = auto_submit.get_agent_worktree_info

def test_tab_switching():
    """Test chuyển tab giữa các model"""
    
    print("🧪 Testing Tab Switching Between Models")
    print("=" * 60)
    
    # Load agents từ shared_state.json
    STATE_FILE = Path(__file__).parent.parent / ".mcp" / "shared_state.json"
    
    if not STATE_FILE.exists():
        print("❌ Không tìm thấy shared_state.json")
        return
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    detected_chats = state.get("detected_chats", [])
    
    if not detected_chats:
        print("⚠️  Không có chat nào đang mở trong session")
        print("   💡 Mở các chat tabs trong Cursor trước khi test")
        return
    
    print(f"📊 Tìm thấy {len(detected_chats)} chats đang mở:")
    for i, chat in enumerate(detected_chats, 1):
        agent_name = chat.get('agent_name', '?')
        worktree_id = chat.get('worktree_id', '?')
        model = chat.get('model', '?')
        print(f"   {i}. {agent_name:20} → {worktree_id:5} ({model})")
    
    print()
    print("🔄 Testing Tab Switching...")
    print()
    
    # Test switch đến từng model
    results = []
    for chat in detected_chats:
        agent_name = chat.get('agent_name')
        worktree_id = chat.get('worktree_id')
        model = chat.get('model')
        chat_id = chat.get('chat_id')
        
        if not model or model == "Unknown":
            print(f"⚠️  {agent_name:20} → Skip (no model)")
            continue
        
        print(f"📌 Testing: {agent_name:20} → {model}")
        print(f"   Worktree ID: {worktree_id}")
        
        # Test switch tab
        result = switch_to_chat_tab(model, worktree_id, chat_id)
        
        status_icon = "✅" if "switched" in result or "already_on_tab" in result else "❌"
        print(f"   {status_icon} Result: {result}")
        
        results.append({
            'agent': agent_name,
            'model': model,
            'worktree_id': worktree_id,
            'result': result,
            'success': "switched" in result or "already_on_tab" in result
        })
        
        print()
        
        # Delay giữa các lần test
        import time
        time.sleep(1.5)
    
    # Summary
    print("=" * 60)
    print("📊 Test Summary:")
    print()
    
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    for r in results:
        status_icon = "✅" if r['success'] else "❌"
        print(f"{status_icon} {r['agent']:20} → {r['model']:30} ({r['result']})")
    
    print()
    print(f"✅ Thành công: {success_count}/{total_count}")
    
    if success_count < total_count:
        print()
        print("💡 Lưu ý:")
        print("   - Nếu 'tab_not_found': Có thể Cursor đang dùng single window mode")
        print("   - Nếu 'app_not_running': Đảm bảo Cursor đang chạy")
        print("   - Nếu 'tab_switch_failed': Có thể tabs không accessible qua AppleScript")

if __name__ == "__main__":
    test_tab_switching()

