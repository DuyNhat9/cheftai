#!/usr/bin/env python3
"""
Test gửi message qua API /api/messages
"""
import requests
import json

API_URL = "http://localhost:8001/api/messages"

def test_send_message():
    """Test gửi message cho Architect"""
    
    payload = {
        "agent": "Architect",
        "chat_id": "qnu",
        "message": "Test message from API",
        "task_id": "TEST",
        "task_title": "Test API Message"
    }
    
    print("📤 Gửi message qua API...")
    print(f"   Agent: {payload['agent']}")
    print(f"   Chat ID: {payload['chat_id']}")
    print(f"   Message: {payload['message']}")
    print()
    
    try:
        response = requests.post(
            API_URL,
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.ok:
            result = response.json()
            print("✅ Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Check auto-submit result
            auto_submit = result.get('auto_submit', {})
            if auto_submit.get('success'):
                print()
                print("✅ Auto-submit thành công!")
            else:
                print()
                print("⚠️  Auto-submit không thành công hoặc bị skip")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Không kết nối được API server")
        print("   💡 Đảm bảo API server đang chạy: python3 .mcp/api_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_send_message()

