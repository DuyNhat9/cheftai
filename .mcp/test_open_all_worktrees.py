#!/usr/bin/env python3
"""Test script để mở full tất cả worktrees"""
import json
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from open_separate_windows import open_or_focus_agent_window

STATE_FILE = Path(__file__).parent.parent / ".mcp" / "shared_state.json"

def main():
    if not STATE_FILE.exists():
        print(f"❌ Không tìm thấy {STATE_FILE}")
        return
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    # Lấy tất cả worktrees từ detected_chats
    detected_chats = state.get('detected_chats', [])
    
    # Nếu không đủ 6, lấy thêm từ agents section
    agents = state.get('agents', {})
    all_worktrees = []
    
    # Thêm từ detected_chats
    for chat in detected_chats:
        all_worktrees.append({
            'agent_name': chat.get('agent_name'),
            'worktree_id': chat.get('worktree_id'),
            'worktree_path': chat.get('worktree_path'),
            'model': chat.get('model'),
            'source': 'detected_chats'
        })
    
    # Thêm từ agents section (nếu chưa có trong detected_chats)
    for agent_name, agent_info in agents.items():
        worktree_id = agent_info.get('worktree_id')
        if worktree_id:
            # Kiểm tra xem đã có trong all_worktrees chưa
            exists = any(wt['worktree_id'] == worktree_id for wt in all_worktrees)
            if not exists:
                all_worktrees.append({
                    'agent_name': agent_name,
                    'worktree_id': worktree_id,
                    'worktree_path': agent_info.get('worktree_path'),
                    'model': agent_info.get('model'),
                    'source': 'agents'
                })
    
    print(f"🧪 Test mở full {len(all_worktrees)} worktrees...")
    print()
    
    # Mở từng worktree
    success_count = 0
    for i, wt in enumerate(all_worktrees[:6], 1):  # Giới hạn 6 worktrees
        agent_name = wt.get('agent_name', 'Unknown')
        worktree_id = wt.get('worktree_id')
        worktree_path = wt.get('worktree_path')
        model = wt.get('model', 'Unknown')
        source = wt.get('source', 'unknown')
        
        print(f"{i}. Mở worktree '{worktree_id}' cho {agent_name} ({source})...")
        print(f"   Path: {worktree_path}")
        
        try:
            result = open_or_focus_agent_window(
                agent_name=agent_name,
                model=model,
                worktree_id=worktree_id,
                worktree_path=worktree_path,
                chat_index=1
            )
            if result:
                print(f"   ✅ Success")
                success_count += 1
            else:
                print(f"   ⚠️  Returned False")
            print()
            
            # Đợi giữa các lần mở để tránh conflict
            if i < len(all_worktrees[:6]):
                time.sleep(2)
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print()
    
    print(f"✅ Hoàn thành: {success_count}/{len(all_worktrees[:6])} worktrees đã mở thành công")

if __name__ == "__main__":
    main()

