#!/usr/bin/env python3
"""Fix chat activity for testing - supports multiple agents"""
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

state_file = Path('.mcp/shared_state.json')
with open(state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)

# Get agent name from command line or default to Backend_AI_Dev
agent_name = sys.argv[1] if len(sys.argv) > 1 else 'Backend_AI_Dev'

agents = state.get('agents', {})
detected_chats = state.get('detected_chats', [])

if agent_name not in agents:
    print(f"❌ Agent {agent_name} not found")
    sys.exit(1)

worktree_id = agents.get(agent_name, {}).get('worktree_id')
print(f'{agent_name} worktree_id: {worktree_id}')

if not worktree_id:
    print(f"❌ No worktree_id for {agent_name}")
    sys.exit(1)

# Update or create chat entry
found = False
for chat in detected_chats:
    if chat.get('worktree_id') == worktree_id:
        chat['agent_name'] = agent_name
        chat['modified_minutes_ago'] = 1.0
        chat['last_active'] = (datetime.now() - timedelta(minutes=1)).isoformat()
        print(f'✅ Updated chat for {agent_name} (worktree {worktree_id})')
        found = True
        break

if not found:
    # Create new chat entry
    detected_chats.append({
        'worktree_id': worktree_id,
        'agent_name': agent_name,
        'modified_minutes_ago': 1.0,
        'last_active': (datetime.now() - timedelta(minutes=1)).isoformat(),
        'model': agents.get(agent_name, {}).get('model', 'Unknown'),
        'worktree_path': f'/Users/davidtran/.cursor/worktrees/cheftAi/{worktree_id}'
    })
    print(f'✅ Created new chat entry for {agent_name}')

# Save
with open(state_file, 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
print('✅ Saved state')

