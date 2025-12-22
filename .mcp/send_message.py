#!/usr/bin/env python3
"""
Script để gửi message từ terminal thông qua API
Usage: python3 send_message.py <agent> <message>
Example: python3 send_message.py Architect "Hello from terminal"
"""
import sys
import json
import subprocess
from pathlib import Path

API_URL = "http://localhost:8001/api/messages"

def send_message(agent: str, message: str):
    """Gửi message qua API"""
    payload = {
        "agent": agent,
        "message": message,
        "task_id": "ADHOC",
        "task_title": "Message from terminal"
    }
    
    try:
        # Dùng curl thay vì requests để không cần install thêm library
        payload_json = json.dumps(payload)
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", API_URL,
             "-H", "Content-Type: application/json",
             "-d", payload_json],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ curl failed: {result.stderr}")
            return 1
        
        result_data = json.loads(result.stdout)
        
        print("✅ Message sent successfully!")
        print(f"   Trigger ID: {result_data.get('trigger_id', 'N/A')}")
        print(f"   Prompt file: {result_data.get('prompt_file', 'N/A')}")
        print(f"   Chat ID: {result_data.get('chat_id', 'N/A')}")
        
        auto_submit = result_data.get('auto_submit', {})
        if auto_submit.get('success'):
            print("   ✅ Auto-submitted to Cursor chat")
            if 'sent_to_cursor_ok' in auto_submit.get('message', ''):
                print("   ✅ Message pasted and submitted successfully")
        else:
            if auto_submit.get('skipped'):
                print("   ⚠️  Auto-submit skipped (not macOS or missing conditions)")
            else:
                print("   ⚠️  Auto-submit failed")
        
        print("\nFull response:")
        print(json.dumps(result_data, indent=2, ensure_ascii=False))
        
        return 0
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse response: {e}")
        print(f"   Response: {result.stdout if 'result' in locals() else 'N/A'}")
        return 1
    except subprocess.TimeoutExpired:
        print("❌ Request timeout after 30s")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 send_message.py <agent> <message>")
        print("Example: python3 send_message.py Architect 'Hello from terminal'")
        print("\nAvailable agents:")
        print("  - Architect")
        print("  - Backend_AI_Dev")
        print("  - UI_UX_Dev")
        print("  - Testing_QA")
        print("  - Supervisor")
        sys.exit(1)
    
    agent = sys.argv[1]
    message = sys.argv[2]
    
    sys.exit(send_message(agent, message))

if __name__ == "__main__":
    main()

