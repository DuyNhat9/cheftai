#!/usr/bin/env python3
"""
Test đơn giản gửi message qua API
"""
import requests
import json

API_URL = "http://localhost:8001/api/messages"

# Test payload
payload = {
    "agent": "Architect",
    "chat_id": "qnu",
    "message": "Test message from API",
    "task_id": "TEST",
    "task_title": "Test API Message"
}

print("📤 Testing API /api/messages")
print("=" * 60)
print(f"Agent: {payload['agent']}")
print(f"Chat ID: {payload['chat_id']}")
print(f"Message: {payload['message']}")
print()

try:
    # Gửi request với timeout ngắn hơn để tránh đợi auto-submit
    response = requests.post(
        API_URL,
        json=payload,
        timeout=10
    )
    
    print(f"✅ Status Code: {response.status_code}")
    print()
    
    if response.ok:
        result = response.json()
        print("📋 Response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print()
        
        # Kiểm tra kết quả
        if result.get('success'):
            print("✅ Message đã được tạo thành công!")
        else:
            print("⚠️  Message creation có vấn đề")
        
        auto_submit = result.get('auto_submit', {})
        if auto_submit:
            if auto_submit.get('success'):
                print("✅ Auto-submit thành công!")
            elif auto_submit.get('skipped'):
                print("⚠️  Auto-submit bị skip (có thể do không phải macOS)")
            else:
                print("⚠️  Auto-submit failed")
    else:
        print(f"❌ Error {response.status_code}:")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("⏱️  Request timeout (có thể do auto-submit mất thời gian)")
    print("   💡 Kiểm tra xem message đã được tạo trong trigger queue chưa")
except requests.exceptions.ConnectionError:
    print("❌ Không kết nối được API server")
    print("   💡 Đảm bảo API server đang chạy: python3 .mcp/api_server.py")
except Exception as e:
    print(f"❌ Error: {e}")

