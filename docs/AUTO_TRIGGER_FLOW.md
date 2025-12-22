# 🔄 Auto-Trigger Flow - Multi-Agent System

## Tổng Quan

Flow tự động hoàn toàn: Chỉ cần ra lệnh cho Architect, các worker agents sẽ tự động được trigger mà không cần bấm "Start" trên dashboard.

## Kiến Trúc

```
┌─────────────────┐
│  Architect      │  (Agent chính - Sonnet 4.5)
│  Cursor Chat    │
└────────┬────────┘
         │
         │ 1. Ra lệnh: "Lên plan cho task X"
         │
         ▼
┌─────────────────┐
│  Architect      │
│  Update         │
│  shared_state   │
│  .json          │
└────────┬────────┘
         │
         │ 2. Thêm tasks với status "PENDING"
         │
         ▼
┌─────────────────┐
│  monitor_service│  (Watchdog - Python)
│  .py            │
│  (Background)   │
└────────┬────────┘
         │
         │ 3. Detect file change
         │    → Tạo prompt files
         │    → Gọi auto_submit_service.py
         │
         ▼
┌─────────────────┐
│  Worker Agents  │
│  (Backend, UI,  │
│   Testing, etc) │
│  Cursor Chats   │
└─────────────────┘
```

## Components

### 1. monitor_service.py

Service chạy background để monitor `shared_state.json`:

- **Watch**: Sử dụng `watchdog` library để detect file changes
- **Process**: Khi có task PENDING mới:
  - Tạo prompt file trong `.mcp/pending_prompts/{agent}.md`
  - Gọi `auto_submit_service.py` để submit vào Cursor chat
  - Update task status → `IN_PROGRESS`
- **Logs**: `/tmp/monitor_service.log`

### 2. auto_submit_service.py

Service để submit prompt vào đúng Cursor chat window:

- Tìm window dựa trên `worktree_id` hoặc `agent_name`
- Focus window và paste prompt
- Submit vào chat

### 3. api_server.py

API server cung cấp endpoints:

- `GET /api/state` - Get shared_state.json (với auto-sync)
- `POST /api/update-task` - Update task status
- `POST /api/messages` - Send message to agent
- `POST /api/notify-change` - Notify monitor (optional)

## Setup

### 1. Install Dependencies

```bash
pip3 install watchdog
```

### 2. Start Services

**Option 1: Start tất cả services cùng lúc**
```bash
./scripts/start_full_system.sh
```

**Option 2: Start từng service**
```bash
# API Server
python3 .mcp/api_server.py > /tmp/api_server.log 2>&1 &

# Dashboard Server
python3 -m http.server 8000 > /tmp/dashboard_server.log 2>&1 &

# Monitor Service
python3 .mcp/monitor_service.py > /tmp/monitor_service.log 2>&1 &
```

### 3. Verify Services

```bash
# Check processes
ps aux | grep -E 'api_server|monitor_service|http.server'

# Check logs
tail -f /tmp/monitor_service.log
```

## Usage

### Step 1: Ra Lệnh cho Architect

Trong Cursor chat với Architect (Sonnet 4.5):

```
Lên plan cho task: [MÔ TẢ TASK]

Yêu cầu:
1. Đọc .mcp/shared_state.json
2. Chia task thành subtasks cho workers
3. Update shared_state.json với tasks PENDING
```

### Step 2: Architect Update shared_state.json

Architect sẽ:
- Phân tích task
- Tạo tasks trong `task_board` với status `"PENDING"`
- Mỗi task có: `id`, `title`, `owner`, `status`, `description`

Ví dụ:
```json
{
  "task_board": [
    {
      "id": "B201",
      "title": "Backend: Implement API endpoint",
      "owner": "Backend_AI_Dev",
      "status": "PENDING",
      "description": "Chi tiết task..."
    }
  ]
}
```

### Step 3: Monitor Service Tự Động Trigger

Monitor service sẽ:
1. Detect file change
2. Tìm tasks PENDING mới
3. Tạo prompt file cho mỗi agent
4. Gọi `auto_submit_service.py` để submit vào Cursor chat
5. Update task status → `IN_PROGRESS`

### Step 4: Workers Làm Việc

Workers nhận prompt và:
- Đọc `shared_state.json`
- Làm task
- Update status → `COMPLETED`

## Monitoring

### View Logs

```bash
# Monitor service logs
tail -f /tmp/monitor_service.log

# API server logs
tail -f /tmp/api_server.log

# Auto-submit logs
tail -f /tmp/auto_submit.log
```

### Check Status

```bash
# Check if monitor is running
pgrep -f monitor_service.py

# Check processed tasks (in monitor logs)
grep "Triggering" /tmp/monitor_service.log
```

## Troubleshooting

### Monitor không trigger

1. **Check monitor đang chạy:**
   ```bash
   pgrep -f monitor_service.py
   ```

2. **Check logs:**
   ```bash
   tail -20 /tmp/monitor_service.log
   ```

3. **Check file permissions:**
   ```bash
   ls -la .mcp/shared_state.json
   ```

4. **Check watchdog installed:**
   ```bash
   python3 -c "import watchdog"
   ```

### Auto-submit không hoạt động

1. **Check Cursor đang chạy:**
   - Cursor app phải đang mở

2. **Check worktree_id mapping:**
   ```bash
   curl -s http://localhost:8001/api/state | python3 -m json.tool | grep worktree_id
   ```

3. **Check auto_submit logs:**
   ```bash
   tail -f /tmp/auto_submit.log
   ```

### Task không được trigger

1. **Check task status:**
   - Phải là `"PENDING"` (không phải `"IN_PROGRESS"` hay `"COMPLETED"`)

2. **Check agent có worktree_id:**
   ```bash
   curl -s http://localhost:8001/api/state | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['agents']['Backend_AI_Dev'].get('worktree_id'))"
   ```

3. **Check processed_tasks:**
   - Monitor service track processed tasks để tránh duplicate
   - Restart monitor để reset: `pkill -f monitor_service.py && ./scripts/start_monitor.sh`

## Best Practices

1. **Task IDs**: Dùng format rõ ràng (e.g., `B201`, `U201`, `Q201`)
2. **Descriptions**: Mô tả chi tiết task để workers hiểu rõ
3. **Dependencies**: Có thể thêm field `dependency` nếu tasks phụ thuộc nhau
4. **Status Flow**: `PENDING` → `IN_PROGRESS` → `COMPLETED`
5. **Error Handling**: Workers nên update status ngay cả khi có lỗi

## Advanced

### Custom Prompt Templates

Có thể customize prompt template trong `monitor_service.py`:

```python
prompt_content = f"""# 🚀 Task Triggered Tự Động
...
"""
```

### Force Trigger

Nếu cần force trigger ngay (không đợi file change):

```bash
# Touch file để trigger monitor
touch .mcp/shared_state.json
```

Hoặc gọi API:
```bash
curl -X POST http://localhost:8001/api/notify-change
```

### Multiple Tasks

Monitor service sẽ trigger tất cả tasks PENDING mới trong một lần file change.

## Summary

✅ **Tự động hoàn toàn**: Chỉ cần ra lệnh cho Architect
✅ **Không cần dashboard**: Monitor service tự động trigger
✅ **Robust**: Track processed tasks, debounce, error handling
✅ **Logging**: Đầy đủ logs để debug

Flow này tái tạo chính xác flow cũ nhưng tự động và robust hơn!

