# Test Gửi Message "dsadads" Cho Từng Model

## Trạng thái hiện tại

- ✅ API server đang chạy tại `http://localhost:8001`
- ✅ Có 6 agents đang active trong `detected_chats`:
  1. Architect (Sonnet 4.5) - worktree_id: qnu
  2. Backend_AI_Dev (GPT-5.1 Codex High Fast) - worktree_id: agd
  3. UI_UX_Dev (claude-4.1-opus) - worktree_id: cqd
  4. Testing_QA (o3 Pro) - worktree_id: ntw
  5. Supervisor (Sonnet 4 1M) - worktree_id: eld
  6. Gemini_3_Pro (Gemini 3 Pro) - chat_id: ff348693-5a66-4c61-b8ca-69ff99780e6e

## Cách test

### Option 1: Qua API (Khuyến nghị)

```bash
# Test gửi cho tất cả agents
python3 .mcp/test_send_message_to_all_models.py "dsadads"

# Hoặc test đơn giản hơn
python3 .mcp/send_dsadads_simple.py
```

### Option 2: Gửi từng agent một qua curl

```bash
# Architect
curl -X POST http://localhost:8001/api/messages \
  -H "Content-Type: application/json" \
  -d '{"agent":"Architect","message":"dsadads","task_id":"TEST"}'

# Backend_AI_Dev
curl -X POST http://localhost:8001/api/messages \
  -H "Content-Type: application/json" \
  -d '{"agent":"Backend_AI_Dev","message":"dsadads","task_id":"TEST"}'

# UI_UX_Dev
curl -X POST http://localhost:8001/api/messages \
  -H "Content-Type: application/json" \
  -d '{"agent":"UI_UX_Dev","message":"dsadads","task_id":"TEST"}'

# Testing_QA
curl -X POST http://localhost:8001/api/messages \
  -H "Content-Type: application/json" \
  -d '{"agent":"Testing_QA","message":"dsadads","task_id":"TEST"}'

# Supervisor
curl -X POST http://localhost:8001/api/messages \
  -H "Content-Type: application/json" \
  -d '{"agent":"Supervisor","message":"dsadads","task_id":"TEST"}'

# Gemini_3_Pro
curl -X POST http://localhost:8001/api/messages \
  -H "Content-Type: application/json" \
  -d '{"agent":"Gemini_3_Pro","message":"dsadads","task_id":"TEST"}'
```

### Option 3: Trực tiếp qua auto_submit_service.py

```bash
# Gửi cho từng agent
python3 .mcp/auto_submit_service.py Architect dsadads qnu
python3 .mcp/auto_submit_service.py Backend_AI_Dev dsadads agd
python3 .mcp/auto_submit_service.py UI_UX_Dev dsadads cqd
python3 .mcp/auto_submit_service.py Testing_QA dsadads ntw
python3 .mcp/auto_submit_service.py Supervisor dsadads eld
python3 .mcp/auto_submit_service.py Gemini_3_Pro dsadads ff348693-5a66-4c61-b8ca-69ff99780e6e
```

## Kết quả test trước đó

- ✅ UI_UX_Dev: Thành công
- ⚠️ Các agents khác: Partial (có thể do tab switching hoặc window focus)

## Lưu ý

- Đảm bảo Cursor đang chạy và các chat windows đang mở
- Nếu timeout, có thể do auto_submit_service.py đang chờ window focus hoặc tab switch
- Kiểm tra logs tại `/tmp/api_server.log` để xem chi tiết
