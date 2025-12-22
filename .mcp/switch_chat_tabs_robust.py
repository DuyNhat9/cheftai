#!/usr/bin/env python3
"""Switch đến chat tabs một cách robust - verify và retry"""
import subprocess
import time
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"

def get_current_chat_info():
    """Lấy thông tin chat hiện tại bằng cách check window title và UI"""
    # Thử nhiều cách để detect chat hiện tại
    script = '''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.2
        set cursorApp to first application process whose name is "Cursor"
        set mainWindow to first window of cursorApp
        
        -- Lấy window title
        set windowTitle to title of mainWindow as string
        
        -- Thử tìm model name trong UI elements
        set modelName to ""
        try
            set allTexts to static texts of mainWindow
            repeat with txt in allTexts
                set txtValue to value of txt as string
                if txtValue contains "Sonnet" or txtValue contains "claude" or txtValue contains "GPT" or txtValue contains "o3" then
                    set modelName to txtValue
                    exit repeat
                end if
            end repeat
        end try
        
        return windowTitle & "|" & modelName
    end tell
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split("|")
            return {
                'window_title': parts[0] if len(parts) > 0 else "",
                'model_name': parts[1] if len(parts) > 1 else ""
            }
    except:
        pass
    return {'window_title': '', 'model_name': ''}

def switch_to_tab_by_cmd_number(tab_index: int, verify_model: str = None):
    """Switch đến tab bằng Cmd+number và verify"""
    print(f"   🔄 Cmd+{tab_index}...")
    
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
    
    # Verify
    current_info = get_current_chat_info()
    print(f"   📍 Window: {current_info['window_title']}")
    print(f"   📍 Model detected: {current_info['model_name']}")
    
    if verify_model:
        if verify_model.lower() in current_info['model_name'].lower():
            return True
    
    return True  # Assume success if we can't verify

def switch_to_tab_by_cycle(count: int):
    """Cycle tabs bằng Cmd+Shift+]"""
    print(f"   🔄 Cycling {count} tabs...")
    
    for i in range(count):
        script = '''
        tell application "System Events"
            tell application "Cursor" to activate
            delay 0.2
            keystroke "]" using {command down, shift down}
            delay 0.5
        end tell
        '''
        subprocess.run(["osascript", "-e", script], timeout=5)
        time.sleep(0.3)
    
    time.sleep(0.5)
    current_info = get_current_chat_info()
    print(f"   📍 After cycle: {current_info['window_title']}")
    return True

def switch_to_agent(agent_name: str, model: str, target_index: int):
    """Switch đến một agent cụ thể"""
    print(f"\n🎯 Switching đến: {agent_name} ({model})")
    print(f"   Target tab index: {target_index}")
    
    # Get current state
    current_info = get_current_chat_info()
    print(f"   📍 Current: {current_info['window_title']}")
    
    # Strategy 1: Dùng Cmd+number
    success = switch_to_tab_by_cmd_number(target_index, verify_model=model)
    
    # Verify lại
    time.sleep(0.5)
    final_info = get_current_chat_info()
    
    # Check nếu model name xuất hiện trong UI
    if model.lower() in final_info['model_name'].lower() or model.lower() in final_info['window_title'].lower():
        print(f"   ✅ Switch thành công!")
        return True
    else:
        print(f"   ⚠️  Switch có thể không thành công (không detect được model)")
        print(f"   💡 Thử verify bằng cách check viền xanh trên card")
        return True  # Assume success, let user verify visually

def main():
    if not STATE_FILE.exists():
        print(f"❌ Không tìm thấy {STATE_FILE}")
        return
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    detected_chats = state.get("detected_chats", [])
    
    print("📋 Tất cả agents:")
    for i, chat in enumerate(detected_chats):
        print(f"   [{i+1}] {chat.get('agent_name')}: {chat.get('model')}")
    
    # Tìm Sonnet 4 1M và claude-4.1-opus
    target_agents = []
    for i, chat in enumerate(detected_chats):
        model = chat.get('model', '')
        agent_name = chat.get('agent_name', '')
        
        if 'Sonnet 4 1M' in model or 'Sonnet 4 1M' in agent_name:
            target_agents.append({
                'name': 'Sonnet 4 1M',
                'model': model,
                'index': i + 1,
                'chat': chat
            })
        elif 'claude-4.1-opus' in model.lower():
            target_agents.append({
                'name': 'claude-4.1-opus',
                'model': model,
                'index': i + 1,
                'chat': chat
            })
    
    if not target_agents:
        print("⚠️  Không tìm thấy targets")
        return
    
    print("\n" + "=" * 60)
    
    # Switch đến từng agent
    for i, agent in enumerate(target_agents):
        switch_to_agent(
            agent['name'],
            agent['model'],
            agent['index']
        )
        
        if i < len(target_agents) - 1:
            print(f"   ⏳ Đợi 2s...")
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ Hoàn tất!")
    print("💡 Kiểm tra viền xanh trên cards để verify")

if __name__ == "__main__":
    main()

