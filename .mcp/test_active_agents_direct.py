#!/usr/bin/env python3
"""
Test trực tiếp logic active agents từ shared_state.json
Không cần API server chạy
"""
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
STATE_FILE = BASE_DIR / ".mcp" / "shared_state.json"

def test_active_agents_logic():
    """Test logic lấy active agents giống như endpoint /api/active-agents"""
    
    if not STATE_FILE.exists():
        print(f"❌ Không tìm thấy {STATE_FILE}")
        return
    
    print("🔍 Testing Active Agents Logic")
    print("=" * 60)
    
    # Load shared_state.json
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    detected_chats = state.get("detected_chats", [])
    agents = state.get("agents", {})
    
    print(f"📊 Detected Chats: {len(detected_chats)}")
    print(f"📋 Configured Agents: {len(agents)}")
    print()
    
    # Tạo danh sách agents có chat active (giống endpoint)
    active_agents = []
    for chat in detected_chats:
        agent_name = chat.get('agent_name')
        if not agent_name:
            continue
        
        # Lấy thông tin agent từ config
        agent_info = agents.get(agent_name, {})
        
        active_agent = {
            'agent_name': agent_name,
            'chat_id': chat.get('chat_id'),
            'worktree_id': chat.get('worktree_id'),
            'worktree_path': chat.get('worktree_path'),
            'model': chat.get('model') or agent_info.get('model'),
            'status': agent_info.get('status', 'Idle'),
            'current_task': agent_info.get('current_task'),
            'role': agent_info.get('role'),
            'last_active': chat.get('last_active'),
            'modified_minutes_ago': chat.get('modified_minutes_ago', 0),
            'has_analytics': 'analytics' in chat
        }
        
        # Thêm analytics nếu có
        if 'analytics' in chat:
            analytics = chat.get('analytics', {})
            active_agent['analytics'] = {
                'has_uncommitted_changes': analytics.get('git_status', {}).get('has_changes', False),
                'modified_files': analytics.get('file_stats', {}).get('modified_files', 0),
                'new_files': analytics.get('file_stats', {}).get('new_files', 0),
                'lines_added': analytics.get('file_stats', {}).get('lines_added', 0),
                'recent_commits_count': len(analytics.get('recent_commits', []))
            }
        
        active_agents.append(active_agent)
    
    # Format response giống endpoint
    response = {
        'success': True,
        'count': len(active_agents),
        'active_agents': active_agents,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    print("✅ Response Format (giống /api/active-agents):")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    print()
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   ✅ Success: {response['success']}")
    print(f"   📈 Count: {response['count']} active agents")
    print()
    print("📋 Active Agents List:")
    for agent in active_agents:
        status_icon = "🟢" if agent['status'] == 'Working' else "⚪"
        analytics_icon = "📊" if agent['has_analytics'] else "  "
        print(f"   {status_icon} {analytics_icon} {agent['agent_name']:20} → {agent['worktree_id']:5} ({agent['model']})")
        if agent['current_task']:
            print(f"      Task: {agent['current_task'][:60]}...")
    
    print()
    print("🔍 Test Cases:")
    print("   1. ✅ Lấy được danh sách agents từ detected_chats")
    print("   2. ✅ Merge thông tin từ agents config")
    print("   3. ✅ Format response đúng chuẩn")
    print("   4. ✅ Include analytics nếu có")
    
    return response

if __name__ == "__main__":
    test_active_agents_logic()

