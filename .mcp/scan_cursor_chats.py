#!/usr/bin/env python3
"""
Scan Cursor IDE windows to detect active chat agents and their models.
macOS only - uses AppleScript to get window titles.
"""
import subprocess
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
STATE_FILE = BASE_DIR / '.mcp' / 'shared_state.json'

def get_cursor_windows():
    """Get all Cursor window titles using AppleScript"""
    script = '''
    tell application "System Events"
        tell process "Cursor"
            set windowList to {}
            repeat with w in windows
                set end of windowList to name of w
            end repeat
            return windowList
        end tell
    end tell
    '''
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Parse AppleScript list output
            output = result.stdout.strip()
            # Output format: "title1, title2, title3"
            if output:
                return [t.strip() for t in output.split(', ')]
        return []
    except Exception as e:
        print(f"Error getting windows: {e}")
        return []

def detect_model_from_title(title):
    """Detect AI model from window title"""
    models = {
        'Sonnet 4.5': 'Sonnet_4.5',
        'Sonnet 4 1M': 'Sonnet_4_1M',
        'GPT-5.1 Codex High Fast': 'GPT_5.1_Codex',
        'claude-4.1-opus': 'Claude_4.1_Opus',
        'o3 Pro': 'o3_Pro',
        'GPT-4': 'GPT_4',
        'Claude': 'Claude',
    }
    for model_name, model_id in models.items():
        if model_name.lower() in title.lower():
            return model_id, model_name
    return None, None

def map_model_to_agent(model_id):
    """Map model to suggested agent role"""
    mapping = {
        'Sonnet_4.5': 'Architect',
        'GPT_5.1_Codex': 'Backend_AI_Dev',
        'Claude_4.1_Opus': 'UI_UX_Dev',
        'o3_Pro': 'Testing_QA',
        'Sonnet_4_1M': 'Supervisor',
    }
    return mapping.get(model_id, 'Unknown')

def scan_and_update():
    """Scan Cursor windows and update shared_state.json"""
    windows = get_cursor_windows()
    
    if not windows:
        print("❌ No Cursor windows found or Cursor not running")
        return
    
    print(f"📊 Found {len(windows)} Cursor window(s):\n")
    
    detected_chats = []
    for i, title in enumerate(windows, 1):
        model_id, model_name = detect_model_from_title(title)
        agent = map_model_to_agent(model_id) if model_id else None
        
        chat_info = {
            'window_index': i,
            'title': title,
            'model_id': model_id,
            'model_name': model_name,
            'suggested_agent': agent
        }
        detected_chats.append(chat_info)
        
        print(f"  {i}. {title}")
        if model_name:
            print(f"     → Model: {model_name}")
            print(f"     → Suggested Agent: {agent}")
        print()
    
    # Update shared_state.json with detected chats
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        # Add detected_chats to state
        state['detected_chats'] = detected_chats
        state['chat_count'] = len(detected_chats)
        
        # Update agents with model info
        for chat in detected_chats:
            agent_name = chat.get('suggested_agent')
            if agent_name and agent_name in state.get('agents', {}):
                state['agents'][agent_name]['model'] = chat.get('model_name')
                state['agents'][agent_name]['window_title'] = chat.get('title')
        
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated shared_state.json with {len(detected_chats)} chat(s)")
    
    return detected_chats

if __name__ == "__main__":
    print("🔍 Scanning Cursor IDE for active chats...\n")
    scan_and_update()

