#!/usr/bin/env python3
"""Check Cursor windows và match với detected_chats"""
import json
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"

# Get all Cursor window titles
script = '''
tell application "System Events"
    try
        set cursorApp to first application process whose name is "Cursor"
        set allTitles to ""
        repeat with aWindow in windows of cursorApp
            try
                set allTitles to allTitles & title of aWindow & "\\n"
            end try
        end repeat
        return allTitles
    on error
        return "Cursor not running"
    end try
end tell
'''

result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
window_titles = result.stdout.strip().split('\n') if result.stdout.strip() else []

print("🔍 Cursor Window Titles:")
print("=" * 60)
for i, title in enumerate(window_titles, 1):
    print(f"  [{i}] {title}")
print()

# Load detected_chats
with open(STATE_FILE, 'r') as f:
    state = json.load(f)

detected_chats = state.get('detected_chats', [])

print("📋 Detected Chats:")
print("=" * 60)
for i, chat in enumerate(detected_chats, 1):
    agent_name = chat.get('agent_name', 'Unknown')
    worktree_id = chat.get('worktree_id', 'N/A')
    model = chat.get('model', 'Unknown')
    print(f"  [{i}] {agent_name:20} → worktree_id: {worktree_id:5} ({model})")
print()

# Check matching
print("🔗 Matching:")
print("=" * 60)
for chat in detected_chats:
    agent_name = chat.get('agent_name')
    worktree_id = chat.get('worktree_id')
    
    # Check if worktree_id appears in any window title
    matched = False
    for title in window_titles:
        if worktree_id and worktree_id in title:
            print(f"  ✅ {agent_name:20} → Found window: '{title}'")
            matched = True
            break
    
    if not matched:
        print(f"  ❌ {agent_name:20} → No window found with worktree_id '{worktree_id}'")

