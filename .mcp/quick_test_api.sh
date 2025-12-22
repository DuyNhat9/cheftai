#!/bin/bash
# Quick test API message

echo "📤 Testing API /api/messages"
echo "============================================================"

python3 << 'PYEOF'
import requests
import json

API_URL = "http://localhost:8001/api/messages"

payload = {
    "agent": "Architect",
    "chat_id": "qnu",
    "message": "Test message from API - testing tab switching improvements",
    "task_id": "TEST",
    "task_title": "Test API Message"
}

print(f"📤 Gửi message:")
print(f"   Agent: {payload['agent']}")
print(f"   Chat ID: {payload['chat_id']}")
print(f"   Message: {payload['message']}")
print()

try:
    response = requests.post(API_URL, json=payload, timeout=15)
    print(f"Status: {response.status_code}")
    print()
    
    if response.ok:
        result = response.json()
        print("✅ Response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        auto_submit = result.get('auto_submit', {})
        if auto_submit.get('success'):
            print()
            print("✅ Auto-submit thành công!")
        else:
            print()
            print("⚠️  Auto-submit:", auto_submit.get('skipped', False) and "Skipped" or "Failed")
    else:
        print(f"❌ Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ API server không chạy")
    print("   💡 Chạy: python3 .mcp/api_server.py")
except requests.exceptions.Timeout:
    print("⏱️  Request timeout (có thể do auto-submit mất thời gian)")
except Exception as e:
    print(f"❌ Error: {e}")
PYEOF

