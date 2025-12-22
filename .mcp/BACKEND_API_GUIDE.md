# 🔌 Backend API Guide - Discover Active Agents

## 📋 Tổng Quan

Backend có thể discover tất cả agents có chat đang mở trong session hiện tại thông qua endpoint `/api/active-agents`.

---

## 🎯 Endpoint: GET `/api/active-agents`

### Mô Tả
Trả về danh sách tất cả agents có chat đang mở trong session hiện tại (từ `detected_chats`).

### Request
```http
GET http://localhost:8001/api/active-agents
Content-Type: application/json
```

### Response Format
```json
{
  "success": true,
  "count": 6,
  "active_agents": [
    {
      "agent_name": "Architect",
      "chat_id": null,
      "worktree_id": "qnu",
      "worktree_path": "/Users/davidtran/.cursor/worktrees/cheftAi/qnu",
      "model": "Sonnet 4.5",
      "status": "Working",
      "current_task": "A200 - Architect: Kiểm tra lại flow Start → Trigger → Auto-submit",
      "role": "Planner - Lên kế hoạch và chia task",
      "last_active": "2025-12-18T22:30:08.928688",
      "modified_minutes_ago": 73.7,
      "has_analytics": true,
      "analytics": {
        "has_uncommitted_changes": true,
        "modified_files": 4,
        "new_files": 89,
        "lines_added": 345,
        "recent_commits_count": 4
      }
    },
    ...
  ],
  "timestamp": "2025-12-19T09:00:00.000000Z"
}
```

### Response Fields

#### Top Level
- `success` (boolean): Request thành công hay không
- `count` (number): Số lượng agents có chat đang mở
- `active_agents` (array): Danh sách agents
- `timestamp` (string): Thời gian response (ISO format)

#### Agent Object
- `agent_name` (string): Tên agent (Architect, Backend_AI_Dev, UI_UX_Dev, Testing_QA, Supervisor, Gemini_3_Pro)
- `chat_id` (string|null): Chat ID (nếu có)
- `worktree_id` (string): Worktree ID (short ID như "qnu", "agd")
- `worktree_path` (string): Đường dẫn đầy đủ đến worktree
- `model` (string): Model AI đang dùng (Sonnet 4.5, GPT-5.1 Codex High Fast, etc.)
- `status` (string): Trạng thái agent ("Working" hoặc "Idle")
- `current_task` (string|null): Task hiện tại đang làm
- `role` (string|null): Vai trò của agent
- `last_active` (string): Thời gian active cuối cùng (ISO format)
- `modified_minutes_ago` (number): Số phút từ lần modify cuối
- `has_analytics` (boolean): Có analytics data hay không
- `analytics` (object|null): Analytics data (nếu có)

---

## 💻 Ví Dụ Sử Dụng

### Python (FastAPI/Flask)
```python
import requests

def get_active_agents():
    """Lấy danh sách agents có chat đang mở"""
    try:
        response = requests.get('http://localhost:8001/api/active-agents', timeout=5)
        if response.ok:
            data = response.json()
            if data.get('success'):
                return data.get('active_agents', [])
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

# Sử dụng
active_agents = get_active_agents()
for agent in active_agents:
    print(f"{agent['agent_name']} → {agent['worktree_id']} ({agent['model']})")
```

### JavaScript/TypeScript (Frontend)
```typescript
async function getActiveAgents() {
  try {
    const response = await fetch('http://localhost:8001/api/active-agents');
    const data = await response.json();
    
    if (data.success) {
      return data.active_agents;
    }
    return [];
  } catch (error) {
    console.error('Error fetching active agents:', error);
    return [];
  }
}

// Sử dụng
const agents = await getActiveAgents();
agents.forEach(agent => {
  console.log(`${agent.agent_name} → ${agent.worktree_id}`);
});
```

### cURL
```bash
curl http://localhost:8001/api/active-agents | jq
```

---

## 🔄 Workflow Đề Xuất

### 1. Discover Agents
```python
# Backend discover agents có chat đang mở
active_agents = get_active_agents()

# Lọc agents theo role nếu cần
backend_agents = [a for a in active_agents if 'Backend' in a.get('role', '')]
ui_agents = [a for a in active_agents if 'UI' in a.get('role', '')]
```

### 2. Gửi Message cho Agents
```python
# Gửi message cho tất cả active agents
for agent in active_agents:
    send_message_to_agent(
        agent_name=agent['agent_name'],
        chat_id=agent['worktree_id'],
        message="Your message here"
    )
```

### 3. Monitor Agent Status
```python
# Polling để monitor agent status
import time

while True:
    active_agents = get_active_agents()
    working_agents = [a for a in active_agents if a['status'] == 'Working']
    print(f"Working agents: {len(working_agents)}")
    time.sleep(5)  # Poll mỗi 5s
```

---

## 📊 Use Cases

### Use Case 1: Broadcast Message
```python
def broadcast_to_all_active_agents(message):
    """Gửi message cho tất cả agents có chat đang mở"""
    active_agents = get_active_agents()
    
    for agent in active_agents:
        requests.post('http://localhost:8001/api/messages', json={
            'agent': agent['agent_name'],
            'chat_id': agent['worktree_id'],
            'message': message,
            'task_id': 'BROADCAST',
            'task_title': 'Broadcast message'
        })
```

### Use Case 2: Find Agent by Role
```python
def find_agent_by_role(role_keyword):
    """Tìm agent theo role"""
    active_agents = get_active_agents()
    
    for agent in active_agents:
        role = agent.get('role', '')
        if role_keyword.lower() in role.lower():
            return agent
    return None

# Tìm Backend agent
backend_agent = find_agent_by_role('Backend')
if backend_agent:
    print(f"Found: {backend_agent['agent_name']} → {backend_agent['worktree_id']}")
```

### Use Case 3: Check Agent Availability
```python
def is_agent_available(agent_name):
    """Kiểm tra agent có chat đang mở và available không"""
    active_agents = get_active_agents()
    
    for agent in active_agents:
        if agent['agent_name'] == agent_name:
            # Agent có chat mở và không đang Working
            return agent['status'] != 'Working'
    return False  # Agent không có chat mở
```

---

## 🔗 Related Endpoints

- `GET /api/state` - Lấy toàn bộ shared_state.json (bao gồm agents và detected_chats)
- `GET /api/agents` - Lấy chỉ agents block (không filter theo detected_chats)
- `POST /api/messages` - Gửi message cho một agent
- `POST /api/scan-worktrees` - Scan và update detected_chats

---

## ⚠️ Lưu Ý

1. **Endpoint chỉ trả về agents có chat trong `detected_chats`**
   - Nếu agent không có chat mở → không xuất hiện trong response
   - Cần chạy `/api/scan-worktrees` trước để update `detected_chats`

2. **Data được lấy từ `shared_state.json`**
   - Đảm bảo file tồn tại và có quyền đọc
   - Data có thể không real-time (cần scan để update)

3. **Analytics chỉ có khi đã chạy analyze**
   - Chạy `/api/analyze-worktrees` để có analytics data
   - `has_analytics` sẽ là `false` nếu chưa analyze

---

## 🧪 Test

```bash
# Test endpoint
python3 .mcp/test_active_agents_api.py

# Hoặc dùng curl
curl http://localhost:8001/api/active-agents | python3 -m json.tool
```

---

**Last Updated:** 2025-12-19  
**Maintained by:** Backend_AI_Dev

