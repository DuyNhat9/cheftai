#!/usr/bin/env python3
"""Switch đến model cards bằng arrow keys"""
import sys
import json
import subprocess
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"

def navigate_to_model_card(current_index: int, target_index: int):
    """Navigate từ current_index đến target_index bằng arrow keys"""
    if current_index == target_index:
        return True
    
    # Tính số lần cần press arrow
    steps = target_index - current_index
    
    print(f"   🔄 Navigate từ card {current_index} → {target_index} ({steps} steps)")
    
    # Dùng Right arrow để đi sang phải, Left arrow để đi sang trái
    arrow_key = "right" if steps > 0 else "left"
    steps = abs(steps)
    
    for i in range(steps):
        script = f'''
        tell application "System Events"
            tell application "Cursor" to activate
            delay 0.1
            key code {63 if arrow_key == "right" else 123}  -- Right: 63, Left: 123
            delay 0.3
        end tell
        '''
        
        try:
            subprocess.run(["osascript", "-e", script], timeout=3)
        except:
            pass
    
    time.sleep(0.5)
    return True

def switch_to_agents():
    """Switch đến Sonnet 4 1M và claude-4.1-opus bằng arrow keys"""
    
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
        print(f"   - {agent['name']} → Card {agent['index']}")
    
    print("\n" + "=" * 60)
    print("💡 Strategy: Dùng arrow keys để navigate giữa model cards")
    print("=" * 60)
    
    # Focus vào Cursor và model selector area
    focus_script = '''
    tell application "System Events"
        tell application "Cursor" to activate
        delay 0.5
        -- Thử Tab để focus vào model selector
        keystroke tab
        delay 0.3
        -- Hoặc Escape để đảm bảo không có popup nào đang mở
        key code 53  -- Escape
        delay 0.2
    end tell
    '''
    subprocess.run(["osascript", "-e", focus_script], timeout=5)
    
    # Giả sử đang ở card đầu tiên (index 1)
    current_index = 1
    
    # Switch đến từng agent
    for i, agent in enumerate(target_agents):
        print(f"\n[{i+1}/{len(target_agents)}] 🔄 Switching đến: {agent['name']}")
        print(f"   Model: {agent['chat'].get('model')}")
        print(f"   Target card: {agent['index']}")
        
        # Navigate đến target card
        navigate_to_model_card(current_index, agent['index'])
        current_index = agent['index']
        
        print(f"   ✅ Đã navigate đến card {agent['index']}")
        print(f"   💡 Kiểm tra viền xanh trên card để verify")
        
        if i < len(target_agents) - 1:
            print(f"   ⏳ Đợi 2s trước khi switch tiếp...")
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ Switch hoàn tất!")
    print("💡 Nếu không hoạt động, có thể cần:")
    print("   1. Focus vào model selector area trước")
    print("   2. Hoặc dùng Tab key để navigate")

if __name__ == "__main__":
    switch_to_agents()

