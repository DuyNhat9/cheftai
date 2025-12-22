#!/usr/bin/env python3
"""Switch đến model cards bằng image detection và click"""
import sys
import json
import time
from pathlib import Path
import importlib.util

PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"

# Import auto_submit_service để dùng image detection functions
auto_submit_path = PROJECT_DIR / '.mcp' / 'auto_submit_service.py'
spec = importlib.util.spec_from_file_location('auto_submit_service', auto_submit_path)
auto_submit_service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auto_submit_service)

def switch_to_model_by_image(model_name: str, agent_name: str):
    """Switch đến model bằng image detection"""
    print(f"\n🎯 Switching đến: {agent_name} ({model_name})")
    
    # Dùng function từ auto_submit_service
    worktree_id = None
    
    # Load từ detected_chats để lấy worktree_id
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
        detected_chats = state.get("detected_chats", [])
        for chat in detected_chats:
            if chat.get('model') == model_name or chat.get('agent_name') == agent_name:
                worktree_id = chat.get('worktree_id')
                break
    
    # Dùng switch_to_chat_tab với image detection
    result = auto_submit_service.switch_to_chat_tab(
        model=model_name,
        worktree_id=worktree_id,
        max_retries=3
    )
    
    if "switched" in result or "already_on_tab" in result:
        print(f"   ✅ Switch thành công!")
        return True
    else:
        print(f"   ❌ Switch failed: {result}")
        
        # Fallback: Thử dùng Cmd+number nếu biết index
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            detected_chats = state.get("detected_chats", [])
            for i, chat in enumerate(detected_chats):
                if chat.get('model') == model_name or chat.get('agent_name') == agent_name:
                    tab_index = i + 1
                    print(f"   🔄 Fallback: Thử Cmd+{tab_index}...")
                    
                    import subprocess
                    script = f'''
                    tell application "System Events"
                        tell application "Cursor" to activate
                        delay 0.3
                        keystroke "{tab_index}" using {{command down}}
                        delay 0.8
                    end tell
                    '''
                    subprocess.run(["osascript", "-e", script], timeout=5)
                    time.sleep(0.5)
                    print(f"   ✅ Đã thử Cmd+{tab_index}")
                    return True
        
        return False

def main():
    if not STATE_FILE.exists():
        print(f"❌ Không tìm thấy {STATE_FILE}")
        return
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    detected_chats = state.get("detected_chats", [])
    
    # Tìm Sonnet 4 1M và claude-4.1-opus
    target_agents = []
    for chat in detected_chats:
        model = chat.get('model', '')
        agent_name = chat.get('agent_name', '')
        
        if 'Sonnet 4 1M' in model:
            target_agents.append({
                'name': 'Sonnet 4 1M',
                'model': model,
                'agent_name': agent_name
            })
        elif 'claude-4.1-opus' in model.lower():
            target_agents.append({
                'name': 'claude-4.1-opus',
                'model': model,
                'agent_name': agent_name
            })
    
    if not target_agents:
        print("⚠️  Không tìm thấy targets")
        return
    
    print("=" * 60)
    print(f"🎯 Tìm thấy {len(target_agents)} agents để switch")
    print("=" * 60)
    
    # Switch đến từng agent
    for i, agent in enumerate(target_agents):
        switch_to_model_by_image(agent['model'], agent['agent_name'])
        
        if i < len(target_agents) - 1:
            print(f"   ⏳ Đợi 2s...")
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ Hoàn tất!")
    print("💡 Kiểm tra viền xanh trên cards để verify")

if __name__ == "__main__":
    main()

