# 📝 Logging System cho CheftAi Multi-Agent

## Tổng quan

Hệ thống logging realtime để debug và monitor các services trong dự án CheftAi.

## Log Files

Các log files được lưu trong `/tmp/`:

- `/tmp/api_server.log` - API server logs (port 8001)
- `/tmp/dashboard_server.log` - Dashboard server logs (port 8000)
- `/tmp/auto_submit.log` - Auto-submit service logs
- `/tmp/cheftai.log` - General logs

## Cách sử dụng

### 1. Monitor tất cả logs (realtime)

```bash
# Cách 1: Dùng script wrapper
./scripts/monitor_logs.sh

# Cách 2: Dùng Python script trực tiếp
python3 .mcp/log_monitor.py
```

### 2. Monitor service cụ thể

```bash
# Chỉ monitor API server
./scripts/monitor_logs.sh -s api

# Chỉ monitor auto-submit
./scripts/monitor_logs.sh -s auto_submit

# Chỉ monitor dashboard
./scripts/monitor_logs.sh -s dashboard
```

### 3. Filter logs

```bash
# Chỉ xem errors
./scripts/monitor_logs.sh --error-only

# Chỉ xem API-related logs
./scripts/monitor_logs.sh --api-only

# Chỉ xem trigger/agent-related logs
./scripts/monitor_logs.sh --trigger-only

# Filter bằng regex pattern
./scripts/monitor_logs.sh -f "trigger|agent"
```

### 4. Kết hợp options

```bash
# Monitor API server, chỉ errors
./scripts/monitor_logs.sh -s api --error-only

# Monitor auto-submit, filter by "cursor"
./scripts/monitor_logs.sh -s auto_submit -f "cursor"
```

## Color Coding

Logs được color-code để dễ đọc:

- 🔴 **Red** - Errors, failures
- 🟡 **Yellow** - Warnings
- 🟢 **Green** - Success messages
- 🔵 **Blue** - Info messages
- 🟣 **Magenta** - Auto-submit related
- 🔵 **Cyan** - API related
- ⚪ **White** - General logs

## Log Format

```
[HH:MM:SS] [SERVICE] [LEVEL] Message
```

Ví dụ:
```
[14:30:15] [API] [INFO] POST /api/messages - Request from 127.0.0.1
[14:30:15] [API] [INFO] 📨 Sending message to agent: Architect, chat_id: qnu, task: ADHOC
[14:30:16] [AUTO_SUBMIT] [INFO] ✅ Auto-submit SUCCESS for Architect
```

## Start Services với Logging

### API Server

```bash
python3 .mcp/api_server.py > /tmp/api_server.log 2>&1 &
```

### Dashboard Server

```bash
python3 .mcp/dashboard_server.py > /tmp/dashboard_server.log 2>&1 &
```

### Auto-submit Service

Auto-submit service tự động ghi log vào `/tmp/auto_submit.log` khi được gọi.

### Start tất cả services

```bash
./scripts/start_full_dashboard.sh
```

Sau đó monitor logs:
```bash
./scripts/monitor_logs.sh
```

## Debug Tips

### 1. Xem logs gần đây

```bash
# Last 50 lines của API server
tail -n 50 /tmp/api_server.log

# Follow log file (realtime)
tail -f /tmp/api_server.log
```

### 2. Tìm errors

```bash
# Tìm tất cả errors trong logs
grep -i "error\|failed\|exception" /tmp/api_server.log

# Tìm errors trong 1 giờ qua
grep -i "error" /tmp/api_server.log | tail -20
```

### 3. Monitor specific endpoint

```bash
# Chỉ xem logs liên quan đến /api/messages
./scripts/monitor_logs.sh -f "/api/messages"
```

### 4. Monitor agent triggers

```bash
# Xem tất cả trigger events
./scripts/monitor_logs.sh --trigger-only
```

## Troubleshooting

### Log files không tồn tại

Nếu log files không tồn tại, có nghĩa là services chưa được start. Start services trước:

```bash
python3 .mcp/api_server.py > /tmp/api_server.log 2>&1 &
```

### Logs không update

1. Kiểm tra services đang chạy:
   ```bash
   ps aux | grep api_server
   ```

2. Kiểm tra log file permissions:
   ```bash
   ls -la /tmp/*.log
   ```

3. Restart service với logging:
   ```bash
   pkill -f api_server
   python3 .mcp/api_server.py > /tmp/api_server.log 2>&1 &
   ```

### Logs quá lớn

Rotate logs định kỳ:

```bash
# Backup và clear log
mv /tmp/api_server.log /tmp/api_server.log.old
touch /tmp/api_server.log
```

Hoặc dùng logrotate (Linux) hoặc tạo cron job.

## Advanced Usage

### Custom filter pattern

```bash
# Filter by multiple patterns
./scripts/monitor_logs.sh -f "trigger|agent|Architect"

# Filter by timestamp (nếu log có timestamp)
./scripts/monitor_logs.sh -f "2025-12-19"
```

### Monitor multiple services

```bash
# Terminal 1: API logs
./scripts/monitor_logs.sh -s api

# Terminal 2: Auto-submit logs
./scripts/monitor_logs.sh -s auto_submit
```

### Export logs

```bash
# Export logs to file
./scripts/monitor_logs.sh > logs_export.txt 2>&1

# Export only errors
./scripts/monitor_logs.sh --error-only > errors.txt 2>&1
```

## Integration với Dashboard

Dashboard có thể hiển thị logs realtime trong tương lai. Hiện tại, dùng terminal monitor là cách tốt nhất để debug.

## Best Practices

1. **Luôn monitor logs khi develop**: Chạy `./scripts/monitor_logs.sh` trong một terminal riêng
2. **Filter khi cần**: Dùng `--error-only` hoặc `-f` để focus vào vấn đề cụ thể
3. **Check logs trước khi commit**: Đảm bảo không có errors trong logs
4. **Rotate logs định kỳ**: Tránh log files quá lớn

---

**Last Updated:** 2025-12-19  
**Maintained by:** Backend_AI_Dev

