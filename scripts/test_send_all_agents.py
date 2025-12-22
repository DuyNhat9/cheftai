#!/usr/bin/env python3
"""
test_send_all_agents.py

Test gửi message đến tất cả agents qua API.
"""

import requests
import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
SHARED_STATE_PATH = PROJECT_DIR / '.mcp' / 'shared_state.json'
AGENT_SERVERS_CONFIG = PROJECT_DIR / '.mcp' / 'agent_servers_config.json'

# Message từ command line hoặc default
message = sys.argv[1] if len(sys.argv) > 1 else "Test message - Xin chào từ hệ thống!"

def get_agent_info():
    """Load agent info từ shared_state.json và agent_servers_config.json"""
    with open(SHARED_STATE_PATH, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    with open(AGENT_SERVERS_CONFIG, 'r', encoding='utf-8') as f:
        servers_config = json.load(f)
    
    agents = {}
    for agent_name, server_info in servers_config.items():
        port = server_info.get('port')
        agent_info = state.get('agents', {}).get(agent_name, {})
        worktree_id = agent_info.get('worktree_id')
        model = agent_info.get('model', 'Unknown')
        
        if port and worktree_id:
            agents[agent_name] = {
                'port': port,
                'worktree_id': worktree_id,
                'model': model
            }
    
    return agents

def send_to_agent(agent_name, port, worktree_id, model, message):
    """Gửi message đến một agent"""
    print(f"\n📤 Sending to {agent_name} ({model})...")
    print(f"   Port: {port}, Worktree: {worktree_id}")
    
    try:
        # Check health
        health_url = f"http://localhost:{port}/health"
        health_response = requests.get(health_url, timeout=2)
        if health_response.status_code != 200:
            print(f"   ❌ Server không healthy: {health_response.status_code}")
            return False
        
        # Send message
        send_url = f"http://localhost:{port}/send_message"
        payload = {
            "message": message,
            "agent_name": agent_name,
            "worktree_id": worktree_id,
            "model": model
        }
        
        response = requests.post(send_url, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Message sent successfully!")
            print(f"   Status: {result.get('status', 'unknown')}")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   {response.text[:100]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Server không chạy trên port {port}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("=== 🧪 TEST GỬI MESSAGE ĐẾN TẤT CẢ AGENTS ===")
    print(f"\nMessage: {message}")
    print()
    
    agents = get_agent_info()
    
    if not agents:
        print("❌ Không tìm thấy agents với port và worktree_id")
        return
    
    print(f"Found {len(agents)} agents:")
    for name in agents.keys():
        print(f"  - {name}")
    
    print("\n" + "="*50)
    
    results = {}
    for agent_name, info in agents.items():
        success = send_to_agent(
            agent_name=agent_name,
            port=info['port'],
            worktree_id=info['worktree_id'],
            model=info['model'],
            message=message
        )
        results[agent_name] = success
    
    # Summary
    print("\n" + "="*50)
    print("=== 📊 KẾT QUẢ ===")
    print()
    
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for agent_name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {agent_name}")
    
    print()
    print(f"Tổng kết: {success_count}/{total_count} agents nhận được message")
    
    if success_count == total_count:
        print("✅ Tất cả agents đã nhận được message!")
    else:
        print("⚠️  Một số agents chưa nhận được message")
        print("   Kiểm tra logs: tail -f /tmp/agent_*.log")

if __name__ == "__main__":
    main()



