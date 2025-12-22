# Agent Servers - Mỗi Agent Như HTTP Server Riêng

## Tổng Quan

Mỗi agent trong hệ thống MCP được expose như một HTTP server riêng trên localhost với port khác nhau, cho phép:
- Gửi request trực tiếp đến từng agent qua HTTP API
- Tích hợp với hệ thống bên ngoài (web app, mobile app)
- Chuẩn bị để scale và phân tán agents sau này

## Kiến Trúc

```
Main API Server (8001)
    ├── Routes to agent servers
    └── Proxy endpoints
         │
         ├── Architect Server (8002)
         ├── Backend Server (8003)
         ├── UI/UX Server (8004)
         └── Testing/QA Server (8005)
```

## Agent Servers

### Ports

- **Architect**: Port 8002
- **Backend_AI_Dev**: Port 8003
- **UI_UX_Dev**: Port 8004
- **Testing_QA**: Port 8005

### Common Endpoints

Tất cả agent servers có các endpoints sau:

#### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "agent": "Architect",
  "port": 8002
}
```

#### `GET /status`

Get agent status từ shared_state.json.

**Response:**
```json
{
  "agent": "Architect",
  "status": "Idle",
  "current_task": null,
  "model": "Sonnet 4.5",
  "role": "Planner - Lên kế hoạch và chia task",
  "worktree_id": "hng"
}
```

#### `POST /process_task`

Process a task cho agent này.

**Request Body:**
```json
{
  "task_id": "T001"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Task T001 started",
  "task": {
    "id": "T001",
    "title": "Task title",
    "status": "IN_PROGRESS",
    ...
  }
}
```

#### `POST /send_message`

Send message đến agent.

**Request Body:**
```json
{
  "message": "Hello, please do this task",
  "task_id": "optional",
  "task_title": "optional"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Message sent",
  "prompt_file": "/path/to/prompt.md",
  "auto_submit": {
    "success": true,
    "stdout": "...",
    "stderr": ""
  }
}
```

#### `GET /tasks`

List tasks của agent này.

**Query Parameters:**
- `status` (optional): Filter by status (PENDING, IN_PROGRESS, COMPLETED)

**Response:**
```json
{
  "agent": "Architect",
  "tasks": [
    {
      "id": "T001",
      "title": "Task title",
      "status": "IN_PROGRESS",
      "owner": "Architect",
      ...
    }
  ],
  "count": 1
}
```

## Main API Server Endpoints

### `GET /api/agent-servers`

List tất cả agent servers từ config.

**Response:**
```json
{
  "Architect": {
    "port": 8002,
    "name": "Architect",
    "server_file": "agents/architect_server.py"
  },
  ...
}
```

### `GET/POST /api/agent/{agent_name}/proxy/{endpoint}`

Proxy request đến agent server.

**Example:**
```bash
# Proxy GET request
curl http://localhost:8001/api/agent/Architect/proxy/health

# Proxy POST request
curl -X POST http://localhost:8001/api/agent/Backend_AI_Dev/proxy/process_task \
  -H "Content-Type: application/json" \
  -d '{"task_id": "T001"}'
```

## Setup

### 1. Install Dependencies

```bash
pip3 install fastapi uvicorn requests
```

### 2. Start Agent Servers

**Option 1: Start tất cả cùng lúc**
```bash
./scripts/start_agent_servers.sh
```

**Option 2: Start từng server**
```bash
python3 .mcp/agents/architect_server.py &
python3 .mcp/agents/backend_server.py &
python3 .mcp/agents/ui_server.py &
python3 .mcp/agents/qa_server.py &
```

**Option 3: Start với full system**
```bash
./scripts/start_full_system.sh
```

### 3. Verify Servers

```bash
# Test health endpoints
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health

# Or use test script
./scripts/test_agent_servers.sh
```

## Usage Examples

### Example 1: Send Message to Agent

```bash
curl -X POST http://localhost:8003/send_message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Please implement search API endpoint",
    "task_id": "B201",
    "task_title": "Backend: Implement search API"
  }'
```

### Example 2: Process Task

```bash
curl -X POST http://localhost:8002/process_task \
  -H "Content-Type: application/json" \
  -d '{"task_id": "A200"}'
```

### Example 3: Get Agent Tasks

```bash
# Get all tasks
curl http://localhost:8004/tasks

# Get only PENDING tasks
curl "http://localhost:8004/tasks?status=PENDING"
```

### Example 4: Use Proxy Endpoint

```bash
# Through main API server
curl http://localhost:8001/api/agent/Architect/proxy/status
```

## Integration với Hệ Thống Hiện Tại

### Shared State

Agent servers đọc và ghi vào `shared_state.json`:
- Load agent info từ `agents` block
- Update task status trong `task_board`
- Update agent status khi process task

### Auto-Submit Service

Khi process task hoặc send message, agent server sẽ:
1. Tạo prompt file trong `.mcp/pending_prompts/`
2. Gọi `auto_submit_service.py` để submit vào Cursor chat
3. Return result về client

### Monitor Service

Monitor service vẫn hoạt động bình thường:
- Detect changes trong `shared_state.json`
- Auto-trigger agents khi có tasks PENDING
- Agent servers có thể được trigger từ monitor hoặc từ API

## Logs

Mỗi agent server có log riêng:
- Architect: `/tmp/agent_Architect.log`
- Backend_AI_Dev: `/tmp/agent_Backend_AI_Dev.log`
- UI_UX_Dev: `/tmp/agent_UI_UX_Dev.log`
- Testing_QA: `/tmp/agent_Testing_QA.log`

## Troubleshooting

### Server không start

1. Check port đã được sử dụng:
   ```bash
   lsof -i :8002
   ```

2. Check logs:
   ```bash
   tail -f /tmp/agent_Architect.log
   ```

3. Check dependencies:
   ```bash
   pip3 list | grep -E "(fastapi|uvicorn)"
   ```

### Request failed

1. Check server đang chạy:
   ```bash
   curl http://localhost:8002/health
   ```

2. Check shared_state.json:
   ```bash
   cat .mcp/shared_state.json | python3 -m json.tool
   ```

3. Check worktree_id trong agent config:
   ```bash
   curl http://localhost:8002/status
   ```

## Future: Scale và Phân Tán

Để deploy agents trên servers khác nhau:

1. Update `agent_servers_config.json`:
   ```json
   {
     "Backend_AI_Dev": {
       "port": 8003,
       "host": "backend-server.example.com",
       "url": "http://backend-server.example.com:8003"
     }
   }
   ```

2. Update proxy logic trong `api_server.py` để sử dụng `url` thay vì localhost

3. Deploy agent server trên remote server

4. Update firewall/security settings

## Summary

- Mỗi agent có HTTP server riêng trên port khác nhau
- Common endpoints: health, status, process_task, send_message, tasks
- Tích hợp với shared_state.json và auto_submit_service.py
- Main API server có proxy endpoints
- Sẵn sàng để scale và phân tán sau này

