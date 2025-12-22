# Cursor Cloud Agents API Setup

## Tổng quan

Hệ thống hỗ trợ **hybrid approach**:
- **Cloud API**: Tự động trigger agents mà không cần mở windows (nếu có API key)
- **Local Fallback**: Sử dụng auto-submit service với windows đã mở (mặc định)

## Setup Cloud API

### 1. Lấy API Key

1. Đăng nhập vào [Cursor Dashboard](https://cursor.com/dashboard?tab=integrations)
2. Tạo API key mới (Basic Auth hoặc Bearer token tùy API)
3. Copy API key

### 2. Cấu hình

1. Copy file config:
   ```bash
   cp .mcp/config.json.example .mcp/config.json
   ```

2. Chỉnh sửa `.mcp/config.json`:
   ```json
   {
     "cursor_cloud_api": {
       "enabled": true,
       "api_key": "your_actual_api_key_here",
       "api_base": "https://api.cursor.com/v0",
       "poll_interval": 10,
       "max_poll_attempts": 60
     },
     "local_fallback": {
       "enabled": true
     }
   }
   ```

3. Restart monitor_service.py:
   ```bash
   pkill -f monitor_service.py
   python3 .mcp/monitor_service.py > /tmp/monitor_service.log 2>&1 &
   ```

## Model Mapping

Hệ thống tự động map local model names sang Cloud API model names:

| Local Model | Cloud API Model |
|------------|-----------------|
| Sonnet 4.5 | claude-4-sonnet |
| GPT-5.1 Codex High Fast | gpt-5.1-codex-high-fast |
| claude-4.1-opus | claude-4.1-opus |
| o3 Pro | o3-pro |
| Sonnet 4 1M | claude-4-sonnet-1m |
| Gemini 3 Pro | gemini-3-pro |

**Lưu ý**: Model names có thể cần adjust dựa trên API thực tế. Check [Cursor API docs](https://docs.cursor.com/background-agent/api/overview) để verify.

## Flow hoạt động

### Với Cloud API enabled:

1. Monitor detect PENDING task
2. Check agent có `cloud_id` chưa
   - Nếu chưa: Launch cloud agent → save `cloud_id`
   - Nếu có: Sử dụng `cloud_id` hiện có
3. Send followup instruction
4. Update task status → IN_PROGRESS
5. (Optional) Poll conversation để check completion

### Với Local Fallback (Cloud API disabled hoặc fail):

1. Monitor detect PENDING task
2. Tạo prompt file
3. Gọi `auto_submit_service.py`
4. Focus window và submit message
5. Update task status → IN_PROGRESS

## Testing

### Test Cloud API:

```bash
# Enable Cloud API trong config.json
# Restart monitor_service
# Tạo PENDING task trong shared_state.json
# Check logs: tail -f /tmp/monitor_service.log
```

### Test Local Fallback:

```bash
# Disable Cloud API trong config.json (enabled: false)
# Restart monitor_service
# Tạo PENDING task
# Verify message xuất hiện trong Cursor chat windows
```

## Troubleshooting

### Cloud API không hoạt động:

1. Check API key đúng chưa
2. Check API base URL (có thể khác với docs)
3. Check network connection
4. Check API rate limits
5. Xem logs: `tail -f /tmp/monitor_service.log | grep cloud_agent`

### Fallback về Local:

- Nếu Cloud API fail, hệ thống tự động fallback về local method
- Đảm bảo Cursor windows đã mở trước khi trigger

## API Endpoints (Expected)

Dựa trên Cursor Background Agent API docs:

- `POST /agents` - Launch new agent
- `POST /agents/{id}/followup` - Send followup instruction
- `GET /agents/{id}/conversation` - Get conversation status

**Lưu ý**: Endpoints có thể khác với docs thực tế. Adjust trong `cloud_agent_client.py` nếu cần.



