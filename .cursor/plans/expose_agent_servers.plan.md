# Expose Agent Servers - Mỗi Agent Như HTTP Server Riêng

## Mục tiêu

Expose mỗi agent trong hệ thống MCP như một HTTP server riêng trên localhost với port khác nhau, cho phép:
- Gửi request trực tiếp đến từng agent qua HTTP API
- Tích hợp với hệ thống bên ngoài (web app, mobile app)
- Chuẩn bị để scale và phân tán agents sau này

## Kiến trúc

```
┌─────────────────┐
│  Main API       │  Port 8001 (existing)
│  api_server.py  │  Routes to agent servers
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │         │          │          │
┌───▼───┐ ┌──▼───┐ ┌───▼───┐ ┌───▼───┐
│Architect│ │Backend│ │UI_UX │ │Testing│
│ Server  │ │Server │ │Server│ │Server │
│ :8002  │ │ :8003 │ │ :8004│ │ :8005 │
└────────┘ └───────┘ └──────┘ └───────┘
    │         │          │          │
    └─────────┴──────────┴──────────┘
              │
    ┌─────────▼─────────┐
    │ shared_state.json │
    │ auto_submit_service│
    └───────────────────┘
```

## Kế hoạch Implementation

### 1. Tạo Base Class cho Agent Server

**File**: `.mcp/agent_server_base.py`

- Base class `AgentServerBase` với FastAPI
- Common endpoints:
  - `GET /health` - Health check
  - `GET /status` - Agent status từ shared_state.json
  - `POST /process_task` - Process task cho agent này
  - `POST /send_message` - Send message đến agent
  - `GET /tasks` - List tasks của agent này
- Shared utilities:
  - Load shared_state.json
  - Call auto_submit_service.py
  - Update task status

### 2. Tạo Individual Agent Servers

**Directory**: `.mcp/agents/`

Tạo các file:
- `architect_server.py` - Port 8002
- `backend_server.py` - Port 8003
- `ui_server.py` - Port 8004
- `qa_server.py` - Port 8005

Mỗi server:
- Extend `AgentServerBase`
- Set agent_name và port
- Agent-specific endpoints nếu cần

### 3. Tạo Config File

**File**: `.mcp/agent_servers_config.json`

```json
{
  "Architect": {"port": 8002, "name": "Architect"},
  "Backend_AI_Dev": {"port": 8003, "name": "Backend_AI_Dev"},
  "UI_UX_Dev": {"port": 8004, "name": "UI_UX_Dev"},
  "Testing_QA": {"port": 8005, "name": "Testing_QA"}
}
```

### 4. Update Main API Server

**File**: `.mcp/api_server.py`

- Thêm endpoint `/api/agent-servers` - List all agent servers
- Thêm endpoint `/api/agent/{agent_name}/proxy` - Proxy request đến agent server
- Load config từ `agent_servers_config.json`

### 5. Tạo Start Script

**File**: `scripts/start_agent_servers.sh`

- Start tất cả agent servers
- Check ports available
- Logs vào `/tmp/agent_{name}.log`
- Graceful shutdown

### 6. Update Full System Script

**File**: `scripts/start_full_system.sh`

- Include agent servers trong startup
- Start sau khi API server ready

### 7. Tạo Test Script

**File**: `scripts/test_agent_servers.sh`

- Test health endpoints
- Test process_task endpoints
- Test send_message endpoints
- Verify integration với shared_state.json

### 8. Documentation

**File**: `docs/AGENT_SERVERS.md`

- Architecture overview
- API endpoints documentation
- Usage examples
- Integration guide

## API Endpoints (Mỗi Agent Server)

### Common Endpoints

- `GET /health` - Health check
  - Response: `{"status": "healthy", "agent": "Architect"}`

- `GET /status` - Agent status
  - Response: Agent info từ shared_state.json

- `POST /process_task` - Process task
  - Body: `{"task_id": "T001"}`
  - Response: `{"success": true, "message": "Task started"}`

- `POST /send_message` - Send message
  - Body: `{"message": "Hello", "task_id": "optional"}`
  - Response: `{"success": true, "trigger_id": "..."}`

- `GET /tasks` - List agent tasks
  - Query: `?status=PENDING|IN_PROGRESS|COMPLETED`
  - Response: List of tasks

## Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `requests` - HTTP client (for proxy)

## Testing Strategy

1. Start all agent servers
2. Test health endpoints
3. Test process_task với task PENDING
4. Verify shared_state.json updated
5. Test send_message
6. Verify auto-submit triggered
7. Test integration với monitor_service.py

## Notes

- Ports: 8002-8005 reserved cho agent servers
- Logs: `/tmp/agent_{name}.log` cho mỗi server
- Integration: Agent servers sử dụng shared_state.json và auto_submit_service.py
- Future: Có thể deploy agents trên servers khác nhau, chỉ cần update config

