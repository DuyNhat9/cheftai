#!/usr/bin/env python3
"""
Detect active chat agents from Cursor worktrees.

Cursor creates a separate worktree for each chat session.
We can detect active sessions by checking:
1. Recently modified worktree index files
2. Agent marker files (.mcp/agent_marker.json) in each worktree

This script scans worktrees, detects active ones, and updates shared_state.json.
"""
import json
import os
import time
from pathlib import Path
from datetime import datetime, timedelta

# Paths
PROJECT_NAME = "cheftAi"
WORKTREES_BASE = Path.home() / ".cursor" / "worktrees" / PROJECT_NAME
MAIN_PROJECT = Path.home() / "Documents" / PROJECT_NAME
GIT_WORKTREES = MAIN_PROJECT / ".git" / "worktrees"
STATE_FILE = MAIN_PROJECT / ".mcp" / "shared_state.json"

# How recent (in minutes) to consider a worktree as "active"
# Tăng threshold để tránh bỏ sót worktree agents ít hoạt động nhưng vẫn cần hiển thị.
# Lưu ý: bước merge phía dưới vẫn ép các agents từ state["agents"] vào detected_chats
# dù không đạt threshold này.
ACTIVE_THRESHOLD_MINUTES = 720  # 12 hours

# Number of most recent worktrees to consider as "active session"
TOP_N_ACTIVE = 5


def get_worktree_modified_times():
    """Get last modified time of each worktree's index file."""
    worktrees = {}
    
    if not GIT_WORKTREES.exists():
        return worktrees
    
    for wt_dir in GIT_WORKTREES.iterdir():
        if wt_dir.is_dir():
            index_file = wt_dir / "index"
            if index_file.exists():
                mtime = datetime.fromtimestamp(index_file.stat().st_mtime)
                worktrees[wt_dir.name] = {
                    "path": str(WORKTREES_BASE / wt_dir.name),
                    "index_modified": mtime.isoformat(),
                    "minutes_ago": (datetime.now() - mtime).total_seconds() / 60
                }
    
    return worktrees


def get_active_worktrees(threshold_minutes=ACTIVE_THRESHOLD_MINUTES, top_n=TOP_N_ACTIVE):
    """
    Get active worktrees using two strategies:
    1. All worktrees modified within threshold_minutes
    2. OR top_n most recently modified (for current session detection)
    
    Returns the union of both, ensuring we capture the current session.
    """
    all_worktrees = get_worktree_modified_times()
    
    if not all_worktrees:
        return {}
    
    # Strategy 1: Within time threshold
    within_threshold = {
        name: info for name, info in all_worktrees.items()
        if info["minutes_ago"] <= threshold_minutes
    }
    
    # Strategy 2: Top N most recent (sorted by minutes_ago ascending)
    sorted_by_recent = sorted(all_worktrees.items(), key=lambda x: x[1]["minutes_ago"])
    top_recent = dict(sorted_by_recent[:top_n])
    
    # Check if top N have similar timestamps (same session)
    if top_recent:
        min_time = min(info["minutes_ago"] for info in top_recent.values())
        max_time = max(info["minutes_ago"] for info in top_recent.values())
        
        # If all top N are within 5 minutes of each other, they're likely same session
        if max_time - min_time <= 5:
            # Use top N as the active session
            return top_recent
    
    # Otherwise return within threshold or top N, whichever is larger
    return within_threshold if len(within_threshold) >= len(top_recent) else top_recent


def read_agent_marker(worktree_path):
    """Read agent marker file if exists in a worktree."""
    marker_file = Path(worktree_path) / ".mcp" / "agent_marker.json"
    
    if marker_file.exists():
        try:
            with open(marker_file, 'r') as f:
                return json.load(f)
        except:
            pass
    
    return None


def detect_agents():
    """Detect active agents from worktrees."""
    active_worktrees = get_active_worktrees()
    
    print(f"🔍 Found {len(active_worktrees)} active worktree(s) (modified within {ACTIVE_THRESHOLD_MINUTES} min):\n")
    
    detected_agents = []
    
    for wt_name, wt_info in sorted(active_worktrees.items(), key=lambda x: x[1]["minutes_ago"]):
        wt_path = wt_info["path"]
        marker = read_agent_marker(wt_path)
        
        agent_info = {
            "worktree_id": wt_name,
            "worktree_path": wt_path,
            "modified_minutes_ago": round(wt_info["minutes_ago"], 1),
            "agent_name": marker.get("agent_name") if marker else None,
            "model": marker.get("model") if marker else None,
            "last_active": wt_info["index_modified"]
        }
        
        detected_agents.append(agent_info)
        
        print(f"  📁 {wt_name}")
        print(f"     Path: {wt_path}")
        print(f"     Modified: {round(wt_info['minutes_ago'], 1)} minutes ago")
        if marker:
            print(f"     Agent: {marker.get('agent_name')} ({marker.get('model')})")
        else:
            print(f"     Agent: Not identified (no marker file)")
        print()
    
    return detected_agents


def update_shared_state(detected_agents):
    """Update shared_state.json with detected agents, preserving existing mappings."""
    if not STATE_FILE.exists():
        print("⚠️ shared_state.json not found")
        return
    
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    # Get existing mappings from old detected_chats
    existing_mappings = {}
    for old_chat in state.get("detected_chats", []):
        wt_id = old_chat.get("worktree_id")
        if wt_id and old_chat.get("agent_name"):
            existing_mappings[wt_id] = {
                "agent_name": old_chat.get("agent_name"),
                "model": old_chat.get("model")
            }
    
    # Also check agents for worktree mappings
    for agent_name, agent_data in state.get("agents", {}).items():
        wt_id = agent_data.get("worktree_id")
        if wt_id and wt_id not in existing_mappings:
            existing_mappings[wt_id] = {
                "agent_name": agent_name,
                "model": agent_data.get("model")
            }
    
    # Apply existing mappings to new detected agents
    for agent in detected_agents:
        wt_id = agent["worktree_id"]
        
        # Priority 1: Read existing marker file (most accurate)
        marker = read_agent_marker(agent["worktree_path"])
        if marker:
            agent["agent_name"] = marker.get("agent_name")
            agent["model"] = marker.get("model")
        # Priority 2: Use existing mapping from shared_state.json
        elif wt_id in existing_mappings:
            agent["agent_name"] = existing_mappings[wt_id]["agent_name"]
            agent["model"] = existing_mappings[wt_id]["model"]
            
            # AUTO-CREATE marker file for future scans (so agents don't need to mark manually)
            try:
                marker_dir = Path(agent["worktree_path"]) / ".mcp"
                marker_dir.mkdir(parents=True, exist_ok=True)
                marker_file = marker_dir / "agent_marker.json"
                
                marker_data = {
                    "agent_name": agent["agent_name"],
                    "model": agent["model"],
                    "created_at": datetime.now().isoformat(),
                    "worktree_path": agent["worktree_path"],
                    "auto_created": True  # Flag to indicate auto-created
                }
                
                with open(marker_file, 'w') as f:
                    json.dump(marker_data, f, indent=2)
                
                print(f"  ✅ Auto-created marker for {wt_id} → {agent['agent_name']} ({agent['model']})")
            except Exception as e:
                print(f"  ⚠️ Could not auto-create marker for {wt_id}: {e}")
    
    # Bổ sung: ép tất cả worktrees từ section agents vào detected_agents (nếu chưa có)
    agents_cfg = state.get("agents", {})
    existing_wt_ids = {a["worktree_id"] for a in detected_agents if a.get("worktree_id")}
    for agent_name, agent_data in agents_cfg.items():
        wt_id = agent_data.get("worktree_id")
        wt_path = agent_data.get("worktree_path")
        model = agent_data.get("model")
        if wt_id and wt_path and wt_id not in existing_wt_ids:
            detected_agents.append({
                "worktree_id": wt_id,
                "worktree_path": wt_path,
                "modified_minutes_ago": agent_data.get("modified_minutes_ago", None) or 0,
                "agent_name": agent_name,
                "model": model,
                "last_active": agent_data.get("last_active", None),
                "from_agents": True
            })
            existing_wt_ids.add(wt_id)
            # Không auto-create marker ở đây (tránh ghi đè), chỉ bổ sung vào detected_chats
            print(f"  ➕ Added from agents config: {wt_id} → {agent_name} ({model})")
    
    # Update detected_chats
    state["detected_chats"] = detected_agents
    state["chat_count"] = len(detected_agents)
    state["last_scan"] = datetime.now().isoformat()
    
    # Update agents with worktree info
    for agent in detected_agents:
        if agent.get("agent_name") and agent["agent_name"] in state.get("agents", {}):
            state["agents"][agent["agent_name"]]["worktree_id"] = agent["worktree_id"]
            state["agents"][agent["agent_name"]]["worktree_path"] = agent["worktree_path"]
            state["agents"][agent["agent_name"]]["last_active"] = agent["last_active"]
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Updated shared_state.json with {len(detected_agents)} detected chat(s)")
    
    # Show mapping status
    mapped = sum(1 for a in detected_agents if a.get("agent_name"))
    print(f"   Mapped: {mapped}/{len(detected_agents)}")


def create_agent_marker(agent_name, model=None):
    """
    Create agent marker file in CURRENT worktree.
    Call this from each agent chat to self-identify.
    """
    # Try to detect current worktree from CWD or environment
    cwd = Path.cwd()
    
    # Check if we're in a worktree
    if ".cursor/worktrees" in str(cwd):
        marker_dir = cwd / ".mcp"
    elif (cwd / ".mcp").exists():
        marker_dir = cwd / ".mcp"
    else:
        # Fallback: use main project
        marker_dir = MAIN_PROJECT / ".mcp"
    
    marker_dir.mkdir(exist_ok=True)
    marker_file = marker_dir / "agent_marker.json"
    
    marker_data = {
        "agent_name": agent_name,
        "model": model,
        "created_at": datetime.now().isoformat(),
        "worktree_path": str(cwd)
    }
    
    with open(marker_file, 'w') as f:
        json.dump(marker_data, f, indent=2)
    
    print(f"✅ Created agent marker: {marker_file}")
    print(f"   Agent: {agent_name}")
    print(f"   Model: {model}")
    
    return marker_file


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "mark" and len(sys.argv) >= 3:
            # Create agent marker: python detect_active_agents.py mark Architect "Sonnet 4.5"
            agent_name = sys.argv[2]
            model = sys.argv[3] if len(sys.argv) > 3 else None
            create_agent_marker(agent_name, model)
        
        elif cmd == "scan":
            # Scan and update
            agents = detect_agents()
            update_shared_state(agents)
        
        else:
            print("Usage:")
            print("  python detect_active_agents.py scan              # Scan active worktrees")
            print("  python detect_active_agents.py mark <agent> [model]  # Mark current worktree")
    else:
        # Default: scan and show
        agents = detect_agents()
        update_shared_state(agents)

