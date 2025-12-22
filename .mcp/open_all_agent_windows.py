#!/usr/bin/env python3
"""
open_all_agent_windows.py

Script để tự động mở tất cả Cursor chat windows cho các agents.
Chạy một lần khi khởi động hệ thống để đảm bảo windows sẵn sàng.
"""

import json
import subprocess
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
SHARED_STATE_PATH = PROJECT_DIR / '.mcp' / 'shared_state.json'


def open_cursor_chat_window(worktree_id: str, model: str, agent_name: str):
    """
    Mở Cursor chat window cho agent cụ thể bằng cách:
    1. Activate Cursor app
    2. Mở chat với Cmd+L hoặc Cmd+I
    3. Switch đến worktree nếu cần
    """
    print(f"📂 Opening window for {agent_name} (model: {model}, worktree: {worktree_id})...")
    
    # AppleScript để mở chat window
    script = f'''
    tell application "System Events"
        try
            set cursorApp to first application process whose name is "Cursor"
        on error
            -- Cursor chưa chạy, activate nó
            tell application "Cursor" to activate
            delay 2.0
            set cursorApp to first application process whose name is "Cursor"
        end try
        
        if not (exists cursorApp) then
            return "app_not_running"
        end if
        
        -- Activate Cursor
        set frontmost of cursorApp to true
        delay 0.5
        
        -- Mở chat bằng Cmd+L (hoặc Cmd+I cho Agent pane)
        -- Thử Cmd+L trước (chat panel)
        keystroke "l" using {{command down}}
        delay 1.0
        
        -- Nếu có worktree, có thể cần switch đến worktree đó
        -- Tuy nhiên, Cursor tự động mở chat trong context hiện tại
        -- Nếu cần switch worktree, có thể dùng cursor CLI:
        -- cursor --goto worktree:{worktree_id}
        
        return "opened"
    end tell
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if "opened" in output:
                print(f"   ✅ Opened chat window for {agent_name}")
                return True
            else:
                print(f"   ⚠️  Could not open window: {output}")
                return False
        else:
            print(f"   ❌ Error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False


def main():
    """Mở tất cả agent windows"""
    if not SHARED_STATE_PATH.exists():
        print(f"❌ shared_state.json not found: {SHARED_STATE_PATH}")
        return
    
    with open(SHARED_STATE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    agents = data.get('agents', {})
    
    print("=== 🚀 Opening All Agent Windows ===")
    print()
    
    opened_count = 0
    for agent_name, agent_info in agents.items():
        worktree_id = agent_info.get('worktree_id')
        model = agent_info.get('model', 'Unknown')
        
        if worktree_id:
            if open_cursor_chat_window(worktree_id, model, agent_name):
                opened_count += 1
            # Delay giữa các windows để Cursor xử lý
            time.sleep(2)
        else:
            print(f"⚠️  Skipping {agent_name}: No worktree_id")
    
    print()
    print(f"=== ✅ Complete: Opened {opened_count}/{len(agents)} agent windows ===")
    print()
    print("💡 Tips:")
    print("   - Windows đã được mở, bạn có thể switch giữa chúng")
    print("   - Monitor service sẽ tự động trigger agents khi có tasks")
    print("   - Chạy script này mỗi khi khởi động hệ thống hoặc restart Cursor")


if __name__ == "__main__":
    main()



