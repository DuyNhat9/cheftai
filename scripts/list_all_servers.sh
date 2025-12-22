#!/bin/bash
# Script để list tất cả servers đang chạy

cd "$(dirname "$0")/.."

echo "=== 📊 DANH SÁCH TẤT CẢ SERVERS ==="
echo ""

# Load shared_state to get model names
python3 << 'PYTHON_SCRIPT'
import json
import urllib.request
import subprocess

# Load shared_state to get model names
with open('.mcp/shared_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)
    agents = state.get('agents', {})

print("🤖 Agent Servers:")
agent_config = {
    8002: "Architect",
    8003: "Backend_AI_Dev",
    8004: "UI_UX_Dev",
    8005: "Testing_QA",
    8006: "Supervisor",
    8007: "Gemini_3_Pro"
}

agent_count = 0
for port, agent_name in agent_config.items():
    try:
        # Get health
        url = f'http://localhost:{port}/health'
        with urllib.request.urlopen(url, timeout=2) as response:
            result = json.loads(response.read().decode('utf-8'))
            status = result.get('status', 'unknown')
        
        # Get model from shared_state
        agent_info = agents.get(agent_name, {})
        model = agent_info.get('model', 'Unknown')
        
        # Get PID
        result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
        pid = result.stdout.strip() if result.returncode == 0 else 'N/A'
        
        print(f"   ✅ {model} ({agent_name}) - Port {port} - PID {pid} - {status}")
        agent_count += 1
    except Exception as e:
        print(f"   ❌ {agent_name} - Port {port} - Not responding")

print()
print("🌐 API & Dashboard Servers:")

# API Server
try:
    result = subprocess.run(['lsof', '-ti', ':8001'], capture_output=True, text=True)
    api_pid = result.stdout.strip() if result.returncode == 0 else None
    if api_pid:
        print(f"   ✅ API Server - Port 8001 - PID {api_pid}")
    else:
        print(f"   ❌ API Server - Port 8001 - Not running")
except:
    print(f"   ❌ API Server - Port 8001 - Not running")

# Dashboard Server
try:
    result = subprocess.run(['lsof', '-ti', ':8000'], capture_output=True, text=True)
    dashboard_pid = result.stdout.strip() if result.returncode == 0 else None
    if dashboard_pid:
        print(f"   ✅ Dashboard Server - Port 8000 - PID {dashboard_pid}")
    else:
        print(f"   ❌ Dashboard Server - Port 8000 - Not running")
except:
    print(f"   ❌ Dashboard Server - Port 8000 - Not running")

print()
print("=== 📊 SUMMARY ===")
print(f"   🤖 Agent Servers: {agent_count}/6")
PYTHON_SCRIPT

# Count API/Dashboard servers
API_COUNT=0
if lsof -ti :8001 >/dev/null 2>&1; then
    API_COUNT=$((API_COUNT + 1))
fi
if lsof -ti :8000 >/dev/null 2>&1; then
    API_COUNT=$((API_COUNT + 1))
fi

echo "   🌐 API/Dashboard Servers: $API_COUNT/2"

# Count total ports
TOTAL=0
for port in 8000 8001 8002 8003 8004 8005 8006 8007; do
    if lsof -ti :$port >/dev/null 2>&1; then
        TOTAL=$((TOTAL + 1))
    fi
done
echo "   📡 Total Ports Active: $TOTAL"

echo ""
echo "📝 Log Files:"
python3 << 'PYTHON_SCRIPT'
import json
import os
import glob

# Load shared_state to get model names
with open('.mcp/shared_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)
    agents = state.get('agents', {})

# Map agent names to model names
agent_to_model = {}
for agent_name, agent_info in agents.items():
    model = agent_info.get('model', 'Unknown')
    agent_to_model[agent_name] = model

# Find all log files
log_files = glob.glob('/tmp/agent_*.log')
for log_file in sorted(log_files):
    # Extract agent name from filename (e.g., /tmp/agent_Architect.log -> Architect)
    filename = os.path.basename(log_file)
    if filename.startswith('agent_') and filename.endswith('.log'):
        agent_name = filename[6:-4]  # Remove 'agent_' prefix and '.log' suffix
        model = agent_to_model.get(agent_name, agent_name)
        
        # Get file size
        size = os.path.getsize(log_file)
        size_str = f"{size}B" if size < 1024 else f"{size/1024:.1f}KB"
        
        print(f"   📄 {model} ({size_str})")
PYTHON_SCRIPT
