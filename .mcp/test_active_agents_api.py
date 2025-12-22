#!/usr/bin/env python3
"""
Test script để verify endpoint /api/active-agents
"""
import requests
import json

API_URL = "http://localhost:8001/api/active-agents"

def test_active_agents_api():
    """Test endpoint /api/active-agents"""
    try:
        response = requests.get(API_URL, timeout=5)
        
        if response.ok:
            data = response.json()
            print("✅ API Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print()
            print(f"📊 Summary:")
            print(f"   - Success: {data.get('success', False)}")
            print(f"   - Count: {data.get('count', 0)} active agents")
            print()
            print("📋 Active Agents:")
            for agent in data.get('active_agents', []):
                print(f"   - {agent.get('agent_name'):20} → {agent.get('worktree_id')} ({agent.get('model')})")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("❌ Không kết nối được API server")
        print("   💡 Đảm bảo API server đang chạy: python3 .mcp/api_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_active_agents_api()

