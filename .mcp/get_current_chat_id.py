#!/usr/bin/env python3
"""
get_current_chat_id.py

Lấy chat ID từ Cursor window hiện tại trên macOS.
Sử dụng AppleScript để lấy window title và extract chat ID.
"""

import subprocess
import json
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"


def get_cursor_window_title():
    """Lấy window title của Cursor window hiện tại."""
    script = '''
    tell application "System Events"
        set cursorApp to first application process whose name is "Cursor"
        set frontWindow to first window of cursorApp
        return title of frontWindow
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
    except Exception as e:
        print(f"Error getting window title: {e}")
    
    return None


def extract_chat_id_from_title(title: str):
    """Extract chat ID từ window title."""
    if not title:
        return None
    
    # Cursor window title có thể chứa chat ID hoặc worktree path
    # Ví dụ: "cheftAi (qnu)" hoặc "cheftAi - Chat ff348693-5a66-4c61-b8ca-69ff99780e6e"
    
    # Tìm UUID pattern
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    match = re.search(uuid_pattern, title, re.IGNORECASE)
    if match:
        return match.group(0)
    
    # Tìm worktree ID trong ngoặc đơn: (qnu), (agd), etc.
    worktree_pattern = r'\(([a-z0-9]{3,})\)'
    match = re.search(worktree_pattern, title)
    if match:
        return match.group(1)
    
    return None


def get_worktree_from_chat_id(chat_id: str):
    """Tìm worktree path từ chat ID."""
    if not chat_id:
        return None
    
    # Nếu là short ID (3-4 ký tự), thử tìm trực tiếp
    if len(chat_id) <= 4:
        worktree_path = Path.home() / ".cursor" / "worktrees" / "cheftAi" / chat_id
        if worktree_path.exists():
            return {
                "worktree_id": chat_id,
                "worktree_path": str(worktree_path)
            }
    
    # Nếu là UUID, tìm trong detected_chats hoặc scan worktrees
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Tìm trong detected_chats
            detected_chats = state.get("detected_chats", [])
            for chat in detected_chats:
                if chat.get("worktree_id") == chat_id:
                    return {
                        "worktree_id": chat.get("worktree_id"),
                        "worktree_path": chat.get("worktree_path")
                    }
            
            # Tìm trong agents
            agents = state.get("agents", {})
            for agent_name, agent_info in agents.items():
                if agent_info.get("worktree_id") == chat_id:
                    return {
                        "worktree_id": agent_info.get("worktree_id"),
                        "worktree_path": agent_info.get("worktree_path")
                    }
        except Exception as e:
            print(f"Error reading shared_state.json: {e}")
    
    # Scan worktrees để tìm UUID trong files
    if len(chat_id) > 10:  # Likely UUID
        worktrees_base = Path.home() / ".cursor" / "worktrees" / "cheftAi"
        if worktrees_base.exists():
            for wt_dir in worktrees_base.iterdir():
                if wt_dir.is_dir():
                    # Check config files
                    config_files = [
                        wt_dir / ".cursor" / "chat.json",
                        wt_dir / ".cursor" / "session.json",
                        wt_dir / ".mcp" / "agent_marker.json",
                    ]
                    for config_file in config_files:
                        if config_file.exists():
                            try:
                                content = config_file.read_text(encoding='utf-8', errors='ignore')
                                if chat_id in content or chat_id[:8] in content:
                                    return {
                                        "worktree_id": wt_dir.name,
                                        "worktree_path": str(wt_dir)
                                    }
                            except:
                                pass
    
    return None


def get_current_cursor_chat_info():
    """Lấy thông tin chat hiện tại từ Cursor window."""
    title = get_cursor_window_title()
    if not title:
        return {
            "success": False,
            "error": "Could not get Cursor window title"
        }
    
    chat_id = extract_chat_id_from_title(title)
    if not chat_id:
        return {
            "success": False,
            "error": f"Could not extract chat ID from title: {title}",
            "window_title": title
        }
    
    worktree_info = get_worktree_from_chat_id(chat_id)
    
    return {
        "success": True,
        "window_title": title,
        "chat_id": chat_id,
        "worktree_info": worktree_info
    }


if __name__ == "__main__":
    import sys
    
    result = get_current_cursor_chat_info()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result.get("success"):
            print(f"✅ Chat ID: {result.get('chat_id')}")
            if result.get("worktree_info"):
                wt = result["worktree_info"]
                print(f"   Worktree ID: {wt.get('worktree_id')}")
                print(f"   Worktree Path: {wt.get('worktree_path')}")
            else:
                print("   ⚠️  Worktree not found")
        else:
            print(f"❌ Error: {result.get('error')}")
            if result.get("window_title"):
                print(f"   Window Title: {result.get('window_title')}")



