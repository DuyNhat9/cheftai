#!/usr/bin/env python3
"""Test nhiều cách switch tabs để tìm cách hoạt động"""
import subprocess
import time
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"

def get_window_title():
    """Lấy window title hiện tại"""
    script = '''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.2
        set cursorApp to first application process whose name is "Cursor"
        set mainWindow to first window of cursorApp
        return title of mainWindow as string
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
            return result.stdout.strip()
    except:
        pass
    return None

def test_method_1_cmd_number(tab_index: int):
    """Method 1: Cmd+1, Cmd+2, etc."""
    print(f"\n📌 Method 1: Cmd+{tab_index}")
    before_title = get_window_title()
    print(f"   Before: {before_title}")
    
    script = f'''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.3
        keystroke "{tab_index}" using {{command down}}
        delay 0.5
    end tell
    '''
    
    subprocess.run(["osascript", "-e", script], timeout=5)
    time.sleep(0.5)
    
    after_title = get_window_title()
    print(f"   After: {after_title}")
    
    return before_title != after_title

def test_method_2_cmd_option_arrows():
    """Method 2: Cmd+Option+Right/Left để cycle"""
    print(f"\n📌 Method 2: Cmd+Option+Right (cycle next)")
    before_title = get_window_title()
    print(f"   Before: {before_title}")
    
    script = '''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.3
        keystroke (character id 124) using {command down, option down}  -- Right arrow
        delay 0.5
    end tell
    '''
    
    subprocess.run(["osascript", "-e", script], timeout=5)
    time.sleep(0.5)
    
    after_title = get_window_title()
    print(f"   After: {after_title}")
    
    return before_title != after_title

def test_method_3_ctrl_tab():
    """Method 3: Ctrl+Tab để cycle"""
    print(f"\n📌 Method 3: Ctrl+Tab")
    before_title = get_window_title()
    print(f"   Before: {before_title}")
    
    script = '''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.3
        keystroke tab using {control down}
        delay 0.5
    end tell
    '''
    
    subprocess.run(["osascript", "-e", script], timeout=5)
    time.sleep(0.5)
    
    after_title = get_window_title()
    print(f"   After: {after_title}")
    
    return before_title != after_title

def test_method_4_cmd_shift_bracket():
    """Method 4: Cmd+Shift+[ hoặc ] để switch tabs"""
    print(f"\n📌 Method 4: Cmd+Shift+] (next tab)")
    before_title = get_window_title()
    print(f"   Before: {before_title}")
    
    script = '''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.3
        keystroke "]" using {command down, shift down}
        delay 0.5
    end tell
    '''
    
    subprocess.run(["osascript", "-e", script], timeout=5)
    time.sleep(0.5)
    
    after_title = get_window_title()
    print(f"   After: {after_title}")
    
    return before_title != after_title

def test_method_5_click_tab_by_ui():
    """Method 5: Click vào tab bằng UI element"""
    print(f"\n📌 Method 5: Click vào tab bằng UI")
    before_title = get_window_title()
    print(f"   Before: {before_title}")
    
    # Thử tìm và click vào tab thứ 2
    script = '''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.3
        set cursorApp to first application process whose name is "Cursor"
        set mainWindow to first window of cursorApp
        
        -- Thử tìm tab buttons
        try
            set tabGroups to groups of mainWindow
            repeat with tg in tabGroups
                try
                    set buttons to buttons of tg
                    if (count of buttons) > 1 then
                        click button 2 of tg
                        delay 0.5
                        exit repeat
                    end if
                end try
            end repeat
        end try
    end tell
    '''
    
    subprocess.run(["osascript", "-e", script], timeout=5)
    time.sleep(0.5)
    
    after_title = get_window_title()
    print(f"   After: {after_title}")
    
    return before_title != after_title

def main():
    print("🧪 Testing các phương pháp switch tabs")
    print("=" * 60)
    
    # Load detected chats để biết có bao nhiêu tabs
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
        detected_chats = state.get("detected_chats", [])
        print(f"📊 Tìm thấy {len(detected_chats)} tabs trong session")
    
    print(f"\n📍 Window title hiện tại: {get_window_title()}")
    
    # Test các methods
    methods = [
        ("Cmd+2", lambda: test_method_1_cmd_number(2)),
        ("Cmd+Option+Right", test_method_2_cmd_option_arrows),
        ("Ctrl+Tab", test_method_3_ctrl_tab),
        ("Cmd+Shift+]", test_method_4_cmd_shift_bracket),
        ("Click UI", test_method_5_click_tab_by_ui),
    ]
    
    results = []
    for name, method in methods:
        try:
            changed = method()
            results.append((name, changed))
            print(f"   {'✅' if changed else '❌'} {name}: {'Changed' if changed else 'No change'}")
            time.sleep(1)
        except Exception as e:
            print(f"   ❌ {name}: Error - {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("📊 Kết quả:")
    working_methods = [name for name, changed in results if changed]
    if working_methods:
        print(f"✅ Methods hoạt động: {', '.join(working_methods)}")
    else:
        print("❌ Không có method nào hoạt động")
    
    print(f"\n📍 Window title cuối cùng: {get_window_title()}")

if __name__ == "__main__":
    main()

