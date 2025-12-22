#!/usr/bin/env python3
"""
Test đơn giản: Switch tab bằng cách dùng Cmd+K và check window title
"""
import subprocess
import time
import json
from pathlib import Path

def test_simple_tab_switch():
    """Test switch tab bằng cách check window title thay đổi"""
    
    print("🧪 Testing Simple Tab Switching")
    print("=" * 60)
    
    # Load detected chats
    STATE_FILE = Path(__file__).parent.parent / ".mcp" / "shared_state.json"
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    detected_chats = state.get("detected_chats", [])
    
    print(f"📊 Testing với {len(detected_chats)} models:")
    print()
    
    for chat in detected_chats[:3]:  # Test 3 đầu tiên
        model = chat.get('model')
        agent_name = chat.get('agent_name')
        
        if not model:
            continue
        
        print(f"📌 Testing: {agent_name} → {model}")
        
        # Get current window title
        script1 = '''
        tell application "System Events"
            set cursorApp to first application process whose name is "Cursor"
            set mainWindow to first window of cursorApp
            return title of mainWindow as string
        end tell
        '''
        
        result1 = subprocess.run(["osascript", "-e", script1], capture_output=True, text=True, timeout=5)
        current_title = result1.stdout.strip()
        print(f"   Current title: {current_title}")
        
        # Try to switch bằng cách tìm window có chứa model name
        # Hoặc dùng Cmd+K để mở chat pane
        script2 = f'''
        tell application "System Events"
            set cursorApp to first application process whose name is "Cursor"
            tell cursorApp
                keystroke "k" using {{command down}}
                delay 0.5
            end tell
            set mainWindow to first window of cursorApp
            return title of mainWindow as string
        end tell
        '''
        
        result2 = subprocess.run(["osascript", "-e", script2], capture_output=True, text=True, timeout=5)
        new_title = result2.stdout.strip()
        print(f"   After Cmd+K: {new_title}")
        
        if model in new_title or model.split()[0] in new_title:
            print(f"   ✅ Model '{model}' found in title!")
        else:
            print(f"   ⚠️  Model '{model}' not found in title")
        
        print()
        time.sleep(1)

if __name__ == "__main__":
    test_simple_tab_switch()

