#!/usr/bin/env python3
"""Test switch đến Sonnet 4 1M và claude-4.1-opus"""
import sys
from pathlib import Path
import importlib.util
import time

PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"

# Import auto_submit_service
auto_submit_path = PROJECT_DIR / '.mcp' / 'auto_submit_service.py'
spec = importlib.util.spec_from_file_location('auto_submit_service', auto_submit_path)
auto_submit_service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auto_submit_service)

def test_switch_to_agents():
    """Test switch đến Sonnet 4 1M và claude-4.1-opus"""
    
    if not STATE_FILE.exists():
        print(f"❌ Không tìm thấy {STATE_FILE}")
        return
    
    import json
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    detected_chats = state.get("detected_chats", [])
    
    # Tìm Sonnet 4 1M và claude-4.1-opus
    target_agents = []
    for chat in detected_chats:
        model = chat.get('model', '')
        agent_name = chat.get('agent_name', '')
        
        if 'Sonnet 4 1M' in model or 'Sonnet 4 1M' in agent_name:
            target_agents.append({
                'name': 'Sonnet 4 1M',
                'chat': chat,
                'model': model,
                'worktree_id': chat.get('worktree_id'),
                'chat_id': chat.get('chat_id')
            })
        elif 'claude-4.1-opus' in model.lower() or 'claude-4.1-opus' in agent_name.lower():
            target_agents.append({
                'name': 'claude-4.1-opus',
                'chat': chat,
                'model': model,
                'worktree_id': chat.get('worktree_id'),
                'chat_id': chat.get('chat_id')
            })
    
    if not target_agents:
        print("⚠️  Không tìm thấy Sonnet 4 1M hoặc claude-4.1-opus trong detected_chats")
        print("\n📋 Tất cả agents hiện có:")
        for chat in detected_chats:
            print(f"   - {chat.get('agent_name')}: {chat.get('model')}")
        return
    
    print(f"🎯 Tìm thấy {len(target_agents)} agents để test switch:")
    for agent in target_agents:
        print(f"   - {agent['name']}: {agent['model']}")
    
    print("\n" + "=" * 60)
    
    # Test switch đến từng agent
    for i, agent in enumerate(target_agents):
        print(f"\n[{i+1}/{len(target_agents)}] 🔄 Testing switch đến: {agent['name']}")
        print(f"   Model: {agent['model']}")
        print(f"   Worktree ID: {agent['worktree_id']}")
        
        result = auto_submit_service.switch_to_chat_tab(
            model=agent['model'],
            worktree_id=agent['worktree_id'],
            chat_id=agent['chat_id'],
            max_retries=3
        )
        
        if "switched" in result or "already_on_tab" in result:
            print(f"   ✅ Switch thành công!")
        else:
            print(f"   ❌ Switch failed: {result}")
        
        if i < len(target_agents) - 1:
            print(f"   ⏳ Đợi 2s trước khi switch tiếp...")
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ Test hoàn tất!")

if __name__ == "__main__":
    test_switch_to_agents()

