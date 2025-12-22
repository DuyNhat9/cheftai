#!/usr/bin/env python3
"""
find_and_map_chat.py

Tìm và map chat ID với worktree.
Có thể map thủ công hoặc tự động tìm từ Cursor window.
"""

import sys
import json
import subprocess
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
    except Exception:
        pass
    
    return None


def list_available_worktrees():
    """Liệt kê tất cả worktrees có sẵn."""
    worktrees_base = Path.home() / ".cursor" / "worktrees" / "cheftAi"
    if not worktrees_base.exists():
        return []
    
    worktrees = []
    for wt_dir in worktrees_base.iterdir():
        if wt_dir.is_dir():
            # Try to get agent info
            marker_file = wt_dir / ".mcp" / "agent_marker.json"
            agent_name = "Unknown"
            model = "Unknown"
            if marker_file.exists():
                try:
                    with open(marker_file, 'r', encoding='utf-8') as f:
                        marker = json.load(f)
                        agent_name = marker.get("agent_name", "Unknown")
                        model = marker.get("model", "Unknown")
                except:
                    pass
            
            worktrees.append({
                "worktree_id": wt_dir.name,
                "worktree_path": str(wt_dir),
                "agent_name": agent_name,
                "model": model
            })
    
    return worktrees


def map_chat_to_worktree(chat_id: str, worktree_id: str = None):
    """Map chat ID với worktree."""
    if not STATE_FILE.exists():
        print("❌ shared_state.json not found")
        return False
    
    # List worktrees
    worktrees = list_available_worktrees()
    
    if not worktree_id:
        # Auto-detect from window title
        window_title = get_cursor_window_title()
        if window_title:
            print(f"📋 Current Cursor window: {window_title}")
            # Extract worktree ID from title (format: "cheftAi (qnu)")
            import re
            match = re.search(r'\(([a-z0-9]{3,})\)', window_title)
            if match:
                worktree_id = match.group(1)
                print(f"✅ Detected worktree ID from window: {worktree_id}")
    
    if not worktree_id:
        # Let user choose
        print(f"\n📋 Available worktrees:")
        for i, wt in enumerate(worktrees, 1):
            print(f"  {i}. {wt['worktree_id']} - {wt['agent_name']} ({wt['model']})")
        
        print(f"\n💡 Chat ID: {chat_id}")
        print("   Enter worktree ID to map (or press Enter to skip): ", end="")
        worktree_id = input().strip()
    
    if not worktree_id:
        print("❌ No worktree selected")
        return False
    
    # Find worktree info
    worktree_info = None
    for wt in worktrees:
        if wt['worktree_id'] == worktree_id:
            worktree_info = wt
            break
    
    if not worktree_info:
        print(f"❌ Worktree {worktree_id} not found")
        return False
    
    # Map using map_chat_to_worktree.py
    try:
        map_script = PROJECT_DIR / ".mcp" / "map_chat_to_worktree.py"
        result = subprocess.run(
            ["python3", str(map_script), chat_id, worktree_id, worktree_info['agent_name'], worktree_info['model']],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ Mapped chat_id {chat_id} to worktree {worktree_id}")
            print(f"   Agent: {worktree_info['agent_name']}")
            print(f"   Model: {worktree_info['model']}")
            return True
        else:
            print(f"❌ Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 find_and_map_chat.py <chat_id> [worktree_id]")
        print("\nExample:")
        print("  python3 find_and_map_chat.py ff348693-5a66-4c61-b8ca-69ff99780e6e")
        print("  python3 find_and_map_chat.py ff348693-5a66-4c61-b8ca-69ff99780e6e qnu")
        sys.exit(1)
    
    chat_id = sys.argv[1]
    worktree_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = map_chat_to_worktree(chat_id, worktree_id)
    sys.exit(0 if success else 1)



