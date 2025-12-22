# 🧪 Test Results - Active Agents API

## ✅ Tests Đã Hoàn Thành

### 1. Endpoint `/api/active-agents` - **PASSED** ✅

**Test:** Lấy danh sách agents có chat đang mở trong session

**Kết quả:**
```json
{
  "success": true,
  "count": 6,
  "active_agents": [
    {
      "agent_name": "Architect",
      "worktree_id": "qnu",
      "model": "Sonnet 4.5",
      "status": "Working",
      "current_task": "A200 - Architect: Kiểm tra lại flow Start → Trigger → Auto-submit"
    },
    {
      "agent_name": "Backend_AI_Dev",
      "worktree_id": "agd",
      "model": "GPT-5.1 Codex High Fast",
      "status": "Working"
    },
    {
      "agent_name": "UI_UX_Dev",
      "worktree_id": "cqd",
      "model": "claude-4.1-opus",
      "status": "Working"
    },
    {
      "agent_name": "Testing_QA",
      "worktree_id": "ntw",
      "model": "o3 Pro",
      "status": "Working"
    },
    {
      "agent_name": "Supervisor",
      "worktree_id": "eld",
      "model": "Sonnet 4 1M",
      "status": "Idle"
    },
    {
      "agent_name": "Gemini_3_Pro",
      "worktree_id": "xcm",
      "model": "Gemini 3 Pro",
      "status": "Idle"
    }
  ]
}
```

**Status:** ✅ **PASSED** - Endpoint hoạt động đúng, trả về đầy đủ thông tin 6 agents

---

### 2. Endpoint `/api/messages` - **IN PROGRESS** ⏳

**Test:** Gửi message "Test message from API" cho Architect

**Payload:**
```json
{
  "agent": "Architect",
  "chat_id": "qnu",
  "message": "Test message from API",
  "task_id": "TEST",
  "task_title": "Test API Message"
}
```

**Status:** ⏳ **IN PROGRESS** - Request có thể bị timeout do auto-submit mất thời gian

**Lưu ý:** 
- API server đang chạy (PID: 82216)
- Endpoint nhận được request
- Auto-submit có thể mất thời gian để focus window và paste message

---

## 📋 Cách Test Thủ Công

### Test 1: Lấy Active Agents
```bash
curl http://localhost:8001/api/active-agents | python3 -m json.tool
```

### Test 2: Gửi Message
```bash
curl -X POST http://localhost:8001/api/messages \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "Architect",
    "chat_id": "qnu",
    "message": "Test message from API",
    "task_id": "TEST",
    "task_title": "Test API Message"
  }'
```

### Test 3: Dùng Python Script
```bash
# Test active agents
python3 .mcp/test_active_agents_direct.py

# Test send message (có thể timeout)
python3 .mcp/test_message_simple.py
```

---

## 🔍 Debugging

Nếu gặp timeout khi gửi message:

1. **Kiểm tra API server đang chạy:**
   ```bash
   lsof -ti:8001
   ```

2. **Kiểm tra logs:**
   ```bash
   tail -f .mcp/api_server.log
   ```

3. **Kiểm tra trigger queue:**
   ```bash
   cat .mcp/trigger_queue.json | python3 -m json.tool
   ```

4. **Kiểm tra pending prompts:**
   ```bash
   ls -la .mcp/pending_prompts/
   ```

---

## ✅ Summary

- ✅ Endpoint `/api/active-agents` hoạt động hoàn hảo
- ⏳ Endpoint `/api/messages` đang test (có thể timeout do auto-submit)
- ✅ Backend routes đã được tạo và đăng ký
- ✅ Logic discovery agents hoạt động đúng

**Next Steps:**
1. Test `/api/messages` với timeout dài hơn
2. Verify message đã được tạo trong trigger queue
3. Verify auto-submit đã gửi message vào Cursor chat

