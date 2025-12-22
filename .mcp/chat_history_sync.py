#!/usr/bin/env python3
"""
Chat History Sync - Lưu và sync chat history giữa các agents
"""
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"

def extract_chat_messages_from_cursor(worktree_id: str, agent_name: str, max_messages: int = 50) -> List[Dict[str, Any]]:
    """
    Extract chat messages từ Cursor window bằng cách đọc chat history.
    Strategy: Dùng AppleScript để đọc chat content từ Cursor UI.
    """
    script = f'''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.5
        set cursorApp to first application process whose name is "Cursor"
        set mainWindow to first window of cursorApp
        
        -- Thử đọc chat messages từ UI
        set chatMessages to {{}}
        
        -- Strategy 1: Đọc từ static texts trong chat area
        try
            set allTexts to static texts of mainWindow
            repeat with txt in allTexts
                try
                    set txtValue to value of txt as string
                    if txtValue is not "" and length of txtValue > 10 then
                        set end of chatMessages to txtValue
                    end if
                end try
            end repeat
        end try
        
        -- Strategy 2: Thử đọc từ text fields
        try
            set allTextFields to text fields of mainWindow
            repeat with txtField in allTextFields
                try
                    set txtValue to value of txtField as string
                    if txtValue is not "" and length of txtValue > 10 then
                        set end of chatMessages to txtValue
                    end if
                end try
            end repeat
        end try
        
        return chatMessages as string
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
            # Parse messages từ output
            messages_text = result.stdout.strip()
            if messages_text:
                # Split by lines và tạo message objects
                messages = []
                lines = messages_text.split('\n')
                for i, line in enumerate(lines[:max_messages]):
                    if line.strip():
                        messages.append({
                            "timestamp": datetime.utcnow().isoformat() + 'Z',
                            "index": i,
                            "content": line.strip(),
                            "role": "assistant" if i % 2 == 0 else "user"  # Guess role
                        })
                return messages
    except Exception as e:
        print(f"[chat_history_sync] Error extracting messages: {e}")
    
    return []

def save_chat_history_to_state(agent_name: str, messages: List[Dict[str, Any]]):
    """
    Lưu chat history vào shared_state.json với file locking.
    """
    if not STATE_FILE.exists():
        return False
    
    # Load state với file locking
    try:
        import fcntl
        with open(STATE_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                state = json.load(f)
                
                # Initialize chat_history section nếu chưa có
                if 'chat_history' not in state:
                    state['chat_history'] = {}
                
                # Update chat history cho agent
                state['chat_history'][agent_name] = {
                    "last_updated": datetime.utcnow().isoformat() + 'Z',
                    "message_count": len(messages),
                    "messages": messages[-50:]  # Keep last 50 messages
                }
                
                # Write back
                f.seek(0)
                f.truncate()
                json.dump(state, f, indent=2, ensure_ascii=False)
                f.flush()
                import os
                os.fsync(f.fileno())
                
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return True
    except Exception as e:
        print(f"[chat_history_sync] Error saving chat history: {e}")
        return False

def sync_all_agents_chat_history():
    """
    Sync chat history cho tất cả agents đang active.
    """
    if not STATE_FILE.exists():
        return
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    detected_chats = state.get("detected_chats", [])
    
    print(f"📥 Syncing chat history cho {len(detected_chats)} agents...")
    
    for chat in detected_chats:
        agent_name = chat.get('agent_name')
        worktree_id = chat.get('worktree_id')
        
        if not agent_name:
            continue
        
        print(f"   📨 Syncing: {agent_name} ({worktree_id})")
        
        # Extract messages
        messages = extract_chat_messages_from_cursor(worktree_id, agent_name)
        
        if messages:
            # Save to state
            if save_chat_history_to_state(agent_name, messages):
                print(f"   ✅ Saved {len(messages)} messages")
            else:
                print(f"   ⚠️  Failed to save messages")
        else:
            print(f"   ⚠️  No messages extracted")
    
    print("✅ Chat history sync completed")

if __name__ == "__main__":
    sync_all_agents_chat_history()

