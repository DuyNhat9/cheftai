#!/usr/bin/env python3
"""Switch đến Sonnet 4 1M và claude-4.1-opus - Fixed version"""
import sys
import json
import subprocess
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"

def get_all_cursor_windows():
    """Lấy tất cả Cursor windows"""
    script = '''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.2
        set cursorApp to first application process whose name is "Cursor"
        set allWindows to windows of cursorApp
        set windowList to {}
        repeat with w in allWindows
            set windowTitle to title of w as string
            set end of windowList to windowTitle
        end repeat
        return windowList as string
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
            titles = result.stdout.strip().split(", ")
            return titles
    except:
        pass
    return []

def focus_window_by_index(index: int):
    """Focus vào window theo index (1-based)"""
    script = f'''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.2
        set cursorApp to first application process whose name is "Cursor"
        set allWindows to windows of cursorApp
        if (count of allWindows) >= {index} then
            set targetWindow to item {index} of allWindows
            set index of targetWindow to 1
            delay 0.5
            return "focused"
        else
            return "window_not_found"
        end if
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
            return "focused" in result.stdout.strip()
    except:
        pass
    return False

def switch_to_model_card_by_keyboard(model_index: int):
    """Switch đến model card bằng Cmd+number (dựa trên thứ tự trong detected_chats)"""
    print(f"   🔄 Dùng Cmd+{model_index} để switch đến model card...")
    
    script = f'''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.3
        keystroke "{model_index}" using {{command down}}
        delay 1.0
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
            print(f"   ✅ Đã gửi Cmd+{model_index}")
            return True
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    return False

def switch_to_agents():
    """Switch đến Sonnet 4 1M và claude-4.1-opus"""
    
    if not STATE_FILE.exists():
        print(f"❌ Không tìm thấy {STATE_FILE}")
        return
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    detected_chats = state.get("detected_chats", [])
    
    print("📋 Tất cả agents hiện có:")
    for i, chat in enumerate(detected_chats):
        print(f"   [{i+1}] {chat.get('agent_name')}: {chat.get('model')}")
    
    print("\n" + "=" * 60)
    
    # Tìm Sonnet 4 1M và claude-4.1-opus
    target_agents = []
    
    for i, chat in enumerate(detected_chats):
        model = chat.get('model', '')
        agent_name = chat.get('agent_name', '')
        
        if 'Sonnet 4 1M' in model or 'Sonnet 4 1M' in agent_name:
            target_agents.append({
                'name': 'Sonnet 4 1M',
                'index': i + 1,
                'chat': chat
            })
        elif 'claude-4.1-opus' in model.lower() or 'claude-4.1-opus' in agent_name.lower():
            target_agents.append({
                'name': 'claude-4.1-opus',
                'index': i + 1,
                'chat': chat
            })
    
    if not target_agents:
        print("⚠️  Không tìm thấy Sonnet 4 1M hoặc claude-4.1-opus")
        return
    
    print(f"🎯 Tìm thấy {len(target_agents)} agents để switch:")
    for agent in target_agents:
        print(f"   - {agent['name']} → Index {agent['index']}")
    
    print("\n" + "=" * 60)
    print("💡 Strategy: Dùng Cmd+1, Cmd+2... để switch đến model cards")
    print("=" * 60)
    
    # Switch đến từng agent bằng Cmd+number
    for i, agent in enumerate(target_agents):
        print(f"\n[{i+1}/{len(target_agents)}] 🔄 Switching đến: {agent['name']}")
        print(f"   Model: {agent['chat'].get('model')}")
        print(f"   Index trong detected_chats: {agent['index']}")
        
        # Dùng Cmd+number để switch đến model card
        success = switch_to_model_card_by_keyboard(agent['index'])
        
        if success:
            print(f"   ✅ Đã switch đến {agent['name']}")
            print(f"   💡 Kiểm tra viền xanh trên card để verify")
        else:
            print(f"   ❌ Switch failed")
        
        if i < len(target_agents) - 1:
            print(f"   ⏳ Đợi 2s trước khi switch tiếp...")
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ Switch hoàn tất!")
    print("💡 Nếu viền xanh không nháy, có thể Cursor không dùng Cmd+number cho model cards")

if __name__ == "__main__":
    switch_to_agents()

