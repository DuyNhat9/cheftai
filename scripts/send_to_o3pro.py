#!/usr/bin/env python3
"""Send message to Testing_QA (o3 Pro) via API"""

import requests
import json
import sys

agent_name = "Testing_QA"
port = 8005
model = "o3 Pro"
worktree_id = "ntw"

# Message từ command line hoặc default
message = sys.argv[1] if len(sys.argv) > 1 else "Xin chào! Bạn có thể giúp tôi test hệ thống không?"

print(f"=== Gửi message đến {agent_name} (o3 Pro) ===")
print(f"Port: {port}")
print(f"Message: {message}")
print()

try:
    # Check health
    health_url = f"http://localhost:{port}/health"
    health_response = requests.get(health_url, timeout=3)
    if health_response.status_code != 200:
        print(f"❌ Server không healthy: {health_response.status_code}")
        sys.exit(1)
    
    print(f"✅ Agent server đang chạy")
    
    # Send message
    send_url = f"http://localhost:{port}/send_message"
    payload = {
        "message": message,
        "agent_name": agent_name,
        "worktree_id": worktree_id,
        "model": model
    }
    
    print(f"📤 Sending to {send_url}...")
    response = requests.post(send_url, json=payload, timeout=15)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Message sent successfully!")
        print(f"   Status: {result.get('status', 'unknown')}")
        if 'message' in result:
            print(f"   Response: {result['message']}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   {response.text}")
        sys.exit(1)
        
except requests.exceptions.ConnectionError:
    print(f"❌ Server không chạy trên port {port}")
    print(f"   Hãy chạy: python3 .mcp/agents/qa_server.py")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)



