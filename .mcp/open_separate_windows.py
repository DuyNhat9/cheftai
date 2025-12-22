#!/usr/bin/env python3
"""Mở separate windows cho mỗi agent"""
import sys
import json
import subprocess
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"

def open_cursor_window_for_worktree(worktree_path: str, worktree_id: str):
    """Mở Cursor window cho một worktree cụ thể và đảm bảo chỉ có 1 chat"""
    print(f"   🔄 Mở window cho worktree: {worktree_path}")
    
    # Strategy 0: Đóng các chat không cần thiết trước (nếu có)
    # Focus vào window chính trước
    try:
        close_other_chats_script = '''
        tell application "System Events"
            tell application "Cursor" to activate
            delay 0.3
            -- Đóng các chat panel không cần thiết bằng Escape
            key code 53  -- Escape để đóng popup/dropdown
            delay 0.2
        end tell
        '''
        subprocess.run(["osascript", "-e", close_other_chats_script], timeout=3)
    except:
        pass
    
    # Strategy 1: Dùng Cursor CLI để mở window mới
    try:
        # Thử dùng cursor command nếu có
        result = subprocess.run(
            ["cursor", worktree_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"   ✅ Đã mở window bằng CLI")
            time.sleep(1.5)  # Đợi window load hoàn toàn
            return True
    except:
        pass
    
    # Strategy 2: Mở bằng AppleScript
    script = f'''
    tell application "Cursor"
        activate
        delay 0.5
        -- Mở folder của worktree (sẽ tạo window mới nếu chưa có)
        open POSIX file "{worktree_path}"
        delay 1.5
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
            print(f"   ✅ Đã mở window bằng AppleScript")
            return True
        else:
            print(f"   ⚠️  Error: {result.stderr}")
    except Exception as e:
        print(f"   ⚠️  Exception: {e}")
    
    return False

def get_all_window_titles():
    """Lấy tất cả window titles để debug"""
    script = '''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.2
        set cursorApp to first application process whose name is "Cursor"
        set allWindows to windows of cursorApp
        set windowTitles to {}
        
        repeat with aWindow in allWindows
            try
                set windowTitle to title of aWindow as string
                set end of windowTitles to windowTitle
            end try
        end repeat
        
        return windowTitles as string
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

def focus_window_by_title(title_keyword: str):
    """Focus vào window có chứa keyword trong title"""
    # Log tất cả window titles để debug
    all_titles = get_all_window_titles()
    if all_titles:
        print(f"   📋 Tất cả window titles: {', '.join(all_titles)}")
    
    script = f'''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.3
        set cursorApp to first application process whose name is "Cursor"
        set allWindows to windows of cursorApp
        
        repeat with aWindow in allWindows
            try
                set windowTitle to title of aWindow as string
                if windowTitle contains "{title_keyword}" then
                    set index of aWindow to 1
                    delay 0.5
                    return "focused"
                end if
            end try
        end repeat
        
        return "not_found"
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

def set_worktree_mode(worktree_id: str):
    """Đảm bảo chế độ worktree được chọn (không phải local)"""
    print(f"   🔧 Đang set worktree mode cho: {worktree_id}")
    
    script = f'''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.5
        
        -- Strategy 1: Đảm bảo chat panel đã mở bằng Cmd+L
        keystroke "l" using {{command down}}
        delay 1.0
        
        -- Strategy 2: Tìm và click vào dropdown "Worktree" để chọn worktree mode
        -- Thử Tab để focus vào worktree dropdown
        keystroke tab
        delay 0.3
        keystroke tab
        delay 0.3
        
        -- Strategy 3: Nếu có dropdown worktree, mở nó và chọn worktree_id
        -- Thử Enter để mở dropdown
        keystroke return
        delay 0.5
        
        -- Strategy 4: Type worktree_id để tìm và chọn
        keystroke "{worktree_id}"
        delay 0.5
        keystroke return
        delay 0.5
        
        -- Strategy 5: Escape để đóng dropdown nếu đã mở
        key code 53  -- Escape
        delay 0.3
    end tell
    '''
    
    try:
        subprocess.run(["osascript", "-e", script], timeout=5)
        print(f"   ✅ Đã set worktree mode")
        return True
    except Exception as e:
        print(f"   ⚠️  Error setting worktree mode: {e}")
        return False

def load_chat_messages(model: str, worktree_id: str = None):
    """Load chat messages bằng cách focus vào chat area và trigger load"""
    print(f"   💬 Đang load chat messages cho model: {model}")
    
    script = f'''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.8
        
        -- Strategy 1: Đảm bảo chat panel đã mở bằng Cmd+L
        keystroke "l" using {{command down}}
        delay 1.0
        
        -- Strategy 2: Focus vào chat input area
        -- Thử Tab nhiều lần để focus vào chat input
        repeat 3 times
            keystroke tab
            delay 0.2
        end repeat
        
        -- Strategy 3: Scroll để trigger load chat history
        -- Scroll lên để load older messages
        key code 116  -- Page Up
        delay 0.5
        key code 116  -- Page Up again
        delay 0.5
        
        -- Scroll về vị trí hiện tại
        key code 121  -- Page Down
        delay 0.3
        
        -- Strategy 4: Thử click vào chat area để trigger load
        -- (Cursor sẽ tự động load khi focus vào chat)
        keystroke return  -- Enter để đảm bảo focus vào chat
        delay 0.3
        
        -- Strategy 5: Thử Escape để clear any popups
        key code 53  -- Escape
        delay 0.3
    end tell
    '''
    
    try:
        subprocess.run(["osascript", "-e", script], timeout=8)
        print(f"   ✅ Đã trigger load chat messages")
        time.sleep(1.0)  # Đợi thêm để chat load
        return True
    except Exception as e:
        print(f"   ⚠️  Error loading chat: {e}")
        return False

def open_or_focus_agent_window(agent_name: str, model: str, worktree_id: str, worktree_path: str, chat_index: int = 1):
    """
    Mở hoặc focus vào window của agent và load chat messages.
    
    Args:
        agent_name: Tên agent
        model: Model name
        worktree_id: Worktree ID
        worktree_path: Đường dẫn worktree
        chat_index: Số thứ tự chat (1 = chat đầu tiên, 2 = chat thứ 2, ...)
                    Nếu chat_index > 1, luôn mở window MỚI cho cùng worktree
    """
    print(f"\n🎯 Agent: {agent_name} ({model})")
    print(f"   Worktree ID: {worktree_id}")
    print(f"   Worktree Path: {worktree_path}")
    print(f"   Chat Index: {chat_index}")
    
    window_opened = False
    
    # Nếu chat_index > 1, luôn mở window MỚI cho cùng worktree (không focus vào window cũ)
    if chat_index > 1:
        print(f"   ➕ Mở chat thứ {chat_index} - sẽ mở window MỚI cho cùng worktree...")
        
        # Strategy: Mở window mới cho cùng worktree
        if worktree_path:
            print(f"   🆕 Mở window mới cho worktree (chat #{chat_index})...")
            if open_cursor_window_for_worktree(worktree_path, worktree_id):
                print(f"   ✅ Đã mở window mới cho chat #{chat_index}")
                time.sleep(2.0)  # Đợi window mới load hoàn toàn
                window_opened = True
            else:
                # Fallback: Dùng Cmd+N để mở window mới
                print(f"   🆕 Fallback: Mở window mới bằng Cmd+N...")
                script = '''
                tell application "System Events"
                    tell application "Cursor" to activate
                    delay 0.5
                    -- Mở window mới bằng Cmd+N
                    keystroke "n" using {command down}
                    delay 2.0
                end tell
                '''
                try:
                    subprocess.run(["osascript", "-e", script], timeout=5)
                    print(f"   ✅ Đã mở window mới bằng Cmd+N")
                    time.sleep(1.0)
                    window_opened = True
                except Exception as e:
                    print(f"   ⚠️  Error opening new window: {e}")
        
        # Sau khi mở window mới, cần navigate đến worktree folder
        if window_opened and worktree_path:
            # Mở folder của worktree trong window mới
            script = f'''
            tell application "System Events"
                tell application "Cursor" to activate
                delay 0.5
                -- Mở folder worktree trong window hiện tại
                keystroke "o" using {{command down}}
                delay 1.0
                keystroke "{worktree_path}"
                delay 0.5
                keystroke return
                delay 1.5
            end tell
            '''
            try:
                subprocess.run(["osascript", "-e", script], timeout=8)
                print(f"   ✅ Đã navigate đến worktree folder trong window mới")
            except Exception as e:
                print(f"   ⚠️  Error navigating to worktree: {e}")
    
    else:
        # chat_index == 1: Tìm window hiện có hoặc mở window mới
        # Strategy 1: Thử focus vào window có chứa worktree_id trong title
        if worktree_id:
            print(f"   🔍 Tìm window có chứa '{worktree_id}'...")
            if focus_window_by_title(worktree_id):
                print(f"   ✅ Đã focus vào window có worktree_id")
                window_opened = True
        
        # Strategy 2: Thử focus vào window có chứa model name
        if not window_opened and model and model != "Unknown":
            model_parts = model.split()
            if len(model_parts) > 0:
                print(f"   🔍 Tìm window có chứa '{model_parts[0]}'...")
                if focus_window_by_title(model_parts[0]):
                    print(f"   ✅ Đã focus vào window có model name")
                    window_opened = True
        
        # Strategy 3: Mở window mới cho worktree
        if not window_opened and worktree_path:
            print(f"   🆕 Mở window mới cho worktree...")
            if open_cursor_window_for_worktree(worktree_path, worktree_id):
                print(f"   ✅ Đã mở window mới")
                time.sleep(1.5)  # Đợi window mở và load
                window_opened = True
        
        # Strategy 4: Thử tạo chat window mới bằng Cmd+L
        if not window_opened:
            print(f"   🆕 Thử tạo chat window mới...")
            script = '''
            tell application "System Events"
                tell application "Cursor" to activate
                delay 0.5
                -- Mở chat mới bằng Cmd+L
                keystroke "l" using {command down}
                delay 1.0
            end tell
            '''
            subprocess.run(["osascript", "-e", script], timeout=5)
            time.sleep(0.5)
            window_opened = True
        
        # Strategy 5: Fallback - focus vào window đầu tiên
        if not window_opened:
            print(f"   ⚠️  Fallback: Focus vào window đầu tiên")
            script = '''
            tell application "System Events"
                tell application "Cursor" to activate
                delay 0.3
                set cursorApp to first application process whose name is "Cursor"
                if (count of windows of cursorApp) > 0 then
                    set firstWindow to first window of cursorApp
                    set index of firstWindow to 1
                    delay 0.5
                end if
            end tell
            '''
            subprocess.run(["osascript", "-e", script], timeout=5)
            window_opened = True
    
    # Sau khi window đã mở/focus, set worktree mode và load chat messages
    if window_opened:
        time.sleep(0.5)  # Đợi window ổn định
        
        # Đảm bảo chế độ worktree được chọn (không phải local)
        if worktree_id:
            set_worktree_mode(worktree_id)
            time.sleep(0.5)
        
        # Load chat messages
        load_chat_messages(model, worktree_id)
    
    return True

def main():
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
    
    # Mở tất cả agents trong detected_chats
    target_agents = []
    for chat in detected_chats:
        agent_name = chat.get('agent_name')
        model = chat.get('model', '')
        
        if agent_name:
            target_agents.append({
                'name': agent_name,
                'model': model,
                'chat': chat
            })
    
    if not target_agents:
        print("⚠️  Không có agents nào trong detected_chats")
        return
    
    print(f"🎯 Tìm thấy {len(target_agents)} agents để mở/focus windows:")
    for i, agent in enumerate(target_agents):
        print(f"   [{i+1}] {agent['name']}: {agent['model']}")
    
    print("\n" + "=" * 60)
    print("💡 Strategy: Mở hoặc focus vào separate window cho mỗi agent")
    print("=" * 60)
    
    # Mở/focus windows cho từng agent
    for i, agent in enumerate(target_agents):
        chat = agent['chat']
        open_or_focus_agent_window(
            agent_name=chat.get('agent_name'),
            model=chat.get('model'),
            worktree_id=chat.get('worktree_id'),
            worktree_path=chat.get('worktree_path')
        )
        
        if i < len(target_agents) - 1:
            print(f"   ⏳ Đợi 2s trước khi mở window tiếp...")
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ Hoàn tất!")
    print("💡 Mỗi agent giờ có thể có window riêng")

if __name__ == "__main__":
    main()

