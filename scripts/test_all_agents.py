#!/usr/bin/env python3
"""
Test script to send messages to all agents
"""
import json
import urllib.request
import time
from pathlib import Path

# Load config
config_file = Path('.mcp/agent_servers_config.json')
with open(config_file, 'r') as f:
    config = json.load(f)

# Load shared_state to get all agents
state_file = Path('.mcp/shared_state.json')
with open(state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)
    all_agents = state.get('agents', {})

print(f'📊 Total agents: {len(all_agents)}')
print(f'📊 Agents with servers: {len(config)}')
print()

success_count = 0
failed_count = 0

# Test send message to each agent that has a server
for agent_name, agent_info in all_agents.items():
    if agent_name in config:
        port = config[agent_name]['port']
        print(f'📤 Sending message to {agent_name} (port {port})...')
        
        url = f'http://localhost:{port}/send_message'
        data = {
            'message': f'Test message từ Agent Server API - {agent_name} - Hệ thống đang test gửi đến tất cả agents',
            'task_id': f'TEST_ALL_{agent_name}',
            'task_title': f'Test Message for {agent_name}'
        }
        
        req = urllib.request.Request(url, 
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'})
        
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))
                if result.get('success'):
                    print(f'   ✅ Success: {result.get("message")}')
                    if result.get('auto_submit', {}).get('success'):
                        print(f'   ✅ Auto-submit: Success')
                    success_count += 1
                else:
                    print(f'   ❌ Failed: {result.get("detail", "Unknown error")}')
                    failed_count += 1
        except Exception as e:
            print(f'   ❌ Error: {str(e)}')
            failed_count += 1
        
        time.sleep(2)  # Delay between messages
    else:
        print(f'⚠️  {agent_name} not in agent_servers_config.json (no server)')
        failed_count += 1

print()
print('=== ✅ TEST SUMMARY ===')
print(f'✅ Success: {success_count}/{len(all_agents)} agents')
print(f'❌ Failed: {failed_count}/{len(all_agents)} agents')
print()
print('🎉 All agents tested!')

