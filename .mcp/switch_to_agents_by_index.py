#!/usr/bin/env python3
"""Switch đến Sonnet 4 1M và claude-4.1-opus bằng keyboard shortcuts (Cmd+1, Cmd+2...)"""
import sys
import json
import subprocess
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"

def switch_by_cmd_number(tab_index: int):
    """Switch đến model card bằng Cmd+number"""
    script = f'''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.3
        keystroke "{tab_index}" using {{command down}}
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
        return result.returncode == 0
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
        return False

def find_agent_index(agent_name: str, model: str):
    """Tìm index của agent trong detected_chats"""
    if not STATE_FILE.exists():
        return None
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    detected_chats = state.get("detected_chats", [])
    
    for i, chat in enumerate(detected_chats):
        chat_agent = chat.get('agent_name', '')
        chat_model = chat.get('model', '')
        
        if agent_name.lower() in chat_agent.lower() or agent_name.lower() in chat_model.lower():
            return i + 1  # Tab index bắt đầu từ 1
        
        if model.lower() in chat_model.lower() or chat_model.lower() in model.lower():
            return i + 1
    
    return None

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
        print(f"   - {agent['name']} → Tab {agent['index']}")
    
    print("\n" + "=" * 60)
    
    # Switch đến từng agent bằng Cmd+number
    print("💡 Strategy: Dùng Cmd+number để switch đến model cards")
    print("=" * 60)
    
    for i, agent in enumerate(target_agents):
        print(f"\n[{i+1}/{len(target_agents)}] 🔄 Switching đến: {agent['name']}")
        print(f"   Model: {agent['chat'].get('model')}")
        print(f"   Index: {agent['index']} → Cmd+{agent['index']}")
        
        success = switch_by_cmd_number(agent['index'])
        
        if success:
            print(f"   ✅ Đã gửi Cmd+{agent['index']}")
            print(f"   💡 Kiểm tra viền xanh trên card để verify")
        else:
            print(f"   ❌ Switch failed")
        
        if i < len(target_agents) - 1:
            print(f"   ⏳ Đợi 2s trước khi switch tiếp...")
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ Switch hoàn tất!")

if __name__ == "__main__":
    switch_to_agents()

