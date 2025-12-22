# Backend API - MCP Integration Guide

Backend API đã được đồng bộ với MCP API server để web có thể gửi messages cho agents.

## Endpoints

### 1. Lấy danh sách active agents

**GET** `/api/agents/active`

Lấy danh sách đầy đủ tất cả agents có chat đang mở trong session.

**Response:**
```json
{
  "active_agents": [
    {
      "agent_name": "Architect",
      "worktree_id": "abc",
      "model": "Sonnet 4.5",
      "status": "active",
      ...
    }
  ],
  "total": 6
}
```

---

### 2. Lấy danh sách active agents (đơn giản)

**GET** `/api/agents/active/simple`

Lấy danh sách đơn giản chỉ với thông tin cơ bản.

**Response:**
```json
{
  "count": 6,
  "agents": [
    {
      "agent_name": "Architect",
      "worktree_id": "abc",
      "model": "Sonnet 4.5",
      "status": "active"
    }
  ]
}
```

---

### 3. Gửi message cho một agent

**POST** `/api/agents/send`

Gửi message cho một agent cụ thể.

**Request Body:**
```json
{
  "agent": "Architect",
  "message": "nhat dang test",
  "task_id": "TEST",  // Optional, default: "ADHOC"
  "task_title": "Test message"  // Optional
}
```

**Response:**
```json
{
  "success": true,
  "agent": "Architect",
  "worktree_id": "abc",
  "auto_submit": {
    "status": "sent_to_cursor_ok",
    ...
  },
  "message": "Message sent successfully"
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/agents/send \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "Architect",
    "message": "nhat dang test"
  }'
```

---

### 4. Broadcast message cho tất cả agents

**POST** `/api/agents/broadcast`

Gửi message cho tất cả agents có chat đang mở.

**Request Body:**
```json
{
  "message": "nhat dang test"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Đã gửi cho 6/6 agents",
  "sent_count": 6,
  "total_count": 6,
  "results": [
    {
      "agent": "Architect",
      "worktree_id": "abc",
      "success": true
    },
    ...
  ]
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/agents/broadcast \
  -H "Content-Type: application/json" \
  -d '{
    "message": "nhat dang test"
  }'
```

---

### 5. Lấy thông tin agent

**GET** `/api/agents/{agent_name}/info`

Lấy thông tin chi tiết của một agent cụ thể.

**Example:**
```bash
curl http://localhost:8000/api/agents/Architect/info
```

---

## Configuration

Backend API sẽ gọi MCP API server tại:
- Default: `http://localhost:8001`
- Có thể override bằng environment variable: `MCP_API_URL`

**Example:**
```bash
export MCP_API_URL=http://localhost:8001
uvicorn app.main:app --reload
```

---

## Web Integration Example

### JavaScript/TypeScript

```javascript
// Gửi message cho một agent
async function sendToAgent(agentName, message) {
  const response = await fetch('http://localhost:8000/api/agents/send', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      agent: agentName,
      message: message
    })
  });
  return await response.json();
}

// Broadcast cho tất cả agents
async function broadcastToAll(message) {
  const response = await fetch('http://localhost:8000/api/agents/broadcast', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message
    })
  });
  return await response.json();
}

// Lấy danh sách active agents
async function getActiveAgents() {
  const response = await fetch('http://localhost:8000/api/agents/active/simple');
  return await response.json();
}
```

---

## Error Handling

Tất cả endpoints sẽ trả về HTTP status codes:
- `200`: Success
- `400`: Bad Request (thiếu required fields)
- `404`: Agent không tìm thấy
- `503`: MCP API server không khả dụng

**Error Response Format:**
```json
{
  "detail": "Error message here"
}
```

---

## Notes

1. **Timeout**: 
   - GET requests: 5 seconds
   - POST requests: 20 seconds (để đủ thời gian cho auto-submit)

2. **MCP API Dependency**: 
   - Backend API phụ thuộc vào MCP API server chạy tại `http://localhost:8001`
   - Đảm bảo MCP API server đang chạy trước khi gọi Backend API

3. **CORS**: 
   - Backend đã cấu hình CORS để cho phép web gọi từ bất kỳ origin nào
   - Trong production, nên restrict origins

