#!/usr/bin/env python3
"""
map_chat_to_worktree.py

Map chat ID với worktree và cập nhật shared_state.json.
Có thể được gọi từ API hoặc CLI.
"""

import sys
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
STATE_FILE = PROJECT_DIR / ".mcp" / "shared_state.json"


def map_chat_to_worktree(chat_id: str, worktree_id: str = None, worktree_path: str = None, agent_name: str = None, model: str = None):
    """Map chat ID với worktree và cập nhật shared_state.json."""
    
    if not STATE_FILE.exists():
        return {"success": False, "error": "shared_state.json not found"}
    
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
    except Exception as e:
        return {"success": False, "error": f"Error reading shared_state.json: {e}"}
    
    # Tìm worktree info nếu chưa có
    if not worktree_id or not worktree_path:
        if worktree_id:
            worktree_path = str(Path.home() / ".cursor" / "worktrees" / "cheftAi" / worktree_id)
        elif worktree_path:
            worktree_id = Path(worktree_path).name
        else:
            # Tìm worktree từ chat_id
            worktrees_base = Path.home() / ".cursor" / "worktrees" / "cheftAi"
            if worktrees_base.exists():
                for wt_dir in worktrees_base.iterdir():
                    if wt_dir.is_dir():
                        config_files = [
                            wt_dir / ".cursor" / "chat.json",
                            wt_dir / ".cursor" / "session.json",
                            wt_dir / ".mcp" / "agent_marker.json",
                        ]
                        for config_file in config_files:
                            if config_file.exists():
                                try:
                                    content = config_file.read_text(encoding='utf-8', errors='ignore')
                                    if chat_id in content or (len(chat_id) > 8 and chat_id[:8] in content):
                                        worktree_id = wt_dir.name
                                        worktree_path = str(wt_dir)
                                        break
                                except:
                                    pass
                        if worktree_id:
                            break
    
    if not worktree_id:
        return {"success": False, "error": "Could not find worktree for chat_id"}
    
    # Cập nhật detected_chats
    detected_chats = state.get("detected_chats", [])
    
    # Tìm xem đã có trong detected_chats chưa
    found = False
    for i, chat in enumerate(detected_chats):
        if chat.get("worktree_id") == worktree_id or chat.get("chat_id") == chat_id:
            # Update existing
            detected_chats[i].update({
                "worktree_id": worktree_id,
                "worktree_path": worktree_path,
                "agent_name": agent_name or chat.get("agent_name", f"Chat_{chat_id[:8]}"),
                "model": model or chat.get("model", "Unknown"),
                "chat_id": chat_id,
            })
            found = True
            break
    
    if not found:
        # Add new
        detected_chats.append({
            "worktree_id": worktree_id,
            "worktree_path": worktree_path,
            "agent_name": agent_name or f"Chat_{chat_id[:8]}",
            "model": model or "Unknown",
            "chat_id": chat_id,
            "modified_minutes_ago": 0,
            "last_active": __import__("datetime").datetime.now().isoformat(),
        })
    
    state["detected_chats"] = detected_chats
    state["chat_count"] = len(detected_chats)
    
    # Cập nhật agents nếu có agent_name
    if agent_name:
        if "agents" not in state:
            state["agents"] = {}
        
        if agent_name not in state["agents"]:
            state["agents"][agent_name] = {}
        
        state["agents"][agent_name].update({
            "worktree_id": worktree_id,
            "worktree_path": worktree_path,
            "model": model or state["agents"][agent_name].get("model", "Unknown"),
            "status": "Idle",
            "last_active": __import__("datetime").datetime.now().isoformat(),
        })
    
    # Save
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "chat_id": chat_id,
            "worktree_id": worktree_id,
            "worktree_path": worktree_path,
            "agent_name": agent_name or f"Chat_{chat_id[:8]}",
        }
    except Exception as e:
        return {"success": False, "error": f"Error saving shared_state.json: {e}"}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 map_chat_to_worktree.py <chat_id> [worktree_id] [agent_name] [model]")
        sys.exit(1)
    
    chat_id = sys.argv[1]
    worktree_id = sys.argv[2] if len(sys.argv) > 2 else None
    agent_name = sys.argv[3] if len(sys.argv) > 3 else None
    model = sys.argv[4] if len(sys.argv) > 4 else None
    
    result = map_chat_to_worktree(chat_id, worktree_id=worktree_id, agent_name=agent_name, model=model)
    
    if result.get("success"):
        print(f"✅ Mapped chat_id {chat_id} to worktree {result.get('worktree_id')}")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error: {result.get('error')}")
        sys.exit(1)



