#!/usr/bin/env python3
"""
Script gửi message với auto test và fix
Tự động kiểm tra và fix các vấn đề trước khi gửi
"""
import sys
import json
import subprocess
import time
from pathlib import Path

API_URL = "http://localhost:8001/api/messages"
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent

def check_api_server():
    """Kiểm tra API server đang chạy"""
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:8001/api/state"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def start_api_server():
    """Start API server"""
    print("   ⚠️  API server không chạy, đang start...")
    subprocess.Popen(
        ["python3", str(SCRIPT_DIR / "api_server.py")],
        cwd=str(PROJECT_DIR),
        stdout=open("/tmp/api_server.log", "w"),
        stderr=subprocess.STDOUT
    )
    # Đợi server start
    for i in range(10):
        time.sleep(0.5)
        if check_api_server():
            print("   ✅ API server đã được start")
            return True
    print("   ❌ Không thể start API server")
    return False

def check_agent_in_state(agent):
    """Kiểm tra agent có trong shared_state không"""
    state_file = PROJECT_DIR / ".mcp" / "shared_state.json"
    if not state_file.exists():
        return False
    
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        agents = state.get('agents', {})
        return agent in agents
    except:
        return False

def scan_worktrees():
    """Scan worktrees để detect agents"""
    print("   ⚠️  Agent chưa có trong shared_state, đang scan worktrees...")
    script = SCRIPT_DIR / "detect_active_agents.py"
    if script.exists():
        result = subprocess.run(
            ["python3", str(script)],
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("   ✅ Đã scan worktrees")
            return True
    print("   ⚠️  Không thể scan worktrees")
    return False

def send_message(agent: str, message: str, max_retries: int = 3):
    """Gửi message với auto retry"""
    payload = {
        "agent": agent,
        "message": message,
        "task_id": "ADHOC",
        "task_title": "Message from terminal"
    }
    
    for attempt in range(max_retries):
        try:
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
                if attempt < max_retries - 1:
                    print(f"   ⚠️  Attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)
                    continue
                else:
                    print(f"   ❌ curl failed: {result.stderr}")
                    return False, None
            
            result_data = json.loads(result.stdout)
            
            if result_data.get('success'):
                return True, result_data
            else:
                if attempt < max_retries - 1:
                    print(f"   ⚠️  Attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)
                    continue
                else:
                    return False, result_data
                    
        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                print(f"   ⚠️  JSON parse error, retrying...")
                time.sleep(2)
                continue
            else:
                print(f"   ❌ Failed to parse response: {e}")
                return False, None
        except subprocess.TimeoutExpired:
            if attempt < max_retries - 1:
                print(f"   ⚠️  Timeout, retrying...")
                time.sleep(2)
                continue
            else:
                print("   ❌ Request timeout")
                return False, None
    
    return False, None

def verify_message(agent):
    """Verify message was sent"""
    prompt_file = PROJECT_DIR / ".mcp" / "pending_prompts" / f"{agent}.md"
    if prompt_file.exists():
        size = prompt_file.stat().st_size
        return True, size
    return False, 0

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 send_message_auto_fix.py <agent> <message>")
        print("Example: python3 send_message_auto_fix.py Architect 'Hello'")
        sys.exit(1)
    
    agent = sys.argv[1]
    message = sys.argv[2]
    
    print("🔍 Auto Test & Fix - Testing message send...")
    
    # Test 1: Kiểm tra API server
    print("\n1️⃣ Checking API server...")
    if not check_api_server():
        if not start_api_server():
            sys.exit(1)
    else:
        print("   ✅ API server đang chạy")
    
    # Test 2: Kiểm tra agent
    print("\n2️⃣ Checking agent in shared_state...")
    if not check_agent_in_state(agent):
        scan_worktrees()
    else:
        print(f"   ✅ Agent '{agent}' có trong shared_state")
    
    # Test 3: Gửi message
    print("\n3️⃣ Sending message...")
    success, result = send_message(agent, message)
    
    if success and result:
        print("   ✅ Message sent successfully!")
        print(f"   Trigger ID: {result.get('trigger_id', 'N/A')}")
        print(f"   Prompt file: {result.get('prompt_file', 'N/A')}")
        print(f"   Chat ID: {result.get('chat_id', 'N/A')}")
        
        auto_submit = result.get('auto_submit', {})
        if auto_submit.get('success'):
            print("   ✅ Auto-submitted to Cursor chat")
            if 'sent_to_cursor_ok' in auto_submit.get('message', ''):
                print("   ✅ Message pasted and submitted successfully")
        else:
            if auto_submit.get('skipped'):
                print("   ⚠️  Auto-submit skipped")
            else:
                print("   ⚠️  Auto-submit failed")
        
        # Test 4: Verify
        print("\n4️⃣ Verifying message...")
        time.sleep(1)
        verified, size = verify_message(agent)
        if verified:
            print(f"   ✅ Prompt file created: {size} bytes")
        else:
            print("   ⚠️  Prompt file not found")
        
        print("\n✅ Auto Test & Fix completed!")
        sys.exit(0)
    else:
        print("   ❌ Failed to send message")
        if result:
            print(f"   Error: {result.get('error', 'Unknown error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()

