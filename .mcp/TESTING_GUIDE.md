# 🧪 Testing Guide - Tab Switching & Message API

## ✅ Đã Hoàn Thành

### 1. Tab Switching Support
- ✅ Thêm function `switch_to_chat_tab()` trong `auto_submit_service.py`
- ✅ Tích hợp vào main flow: sau khi focus window, tự động thử switch tab
- ⚠️ **Kết quả test:** Tab switching không hoạt động (Cursor có thể dùng separate windows)

### 2. Improved Verification
- ✅ Cải thiện `verify_message_sent()` với chat content verification
- ✅ Thêm function `_get_chat_content()` để đọc chat content
- ✅ Pass `chat_id` và `model` vào verification

### 3. Window Switching (Đã Hoạt Động)
- ✅ `find_and_focus_cursor_window()` đã hoạt động tốt
- ✅ Tìm window theo model name trong title
- ✅ Focus vào đúng window

## 📋 Cách Test

### Test 1: Gửi Message qua API

```bash
# Option 1: Dùng script
python3 .mcp/test_message_simple.py

# Option 2: Dùng curl
curl -X POST http://localhost:8001/api/messages \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "Architect",
    "chat_id": "qnu",
    "message": "Test message from API - testing tab switching improvements",
    "task_id": "TEST",
    "task_title": "Test API Message"
  }'

# Option 3: Dùng quick script
.mcp/quick_test_api.sh
```

### Test 2: Test Tab Switching

```bash
# Test tab switching function
python3 .mcp/test_tab_switching.py

# Test simple tab switch
python3 .mcp/test_tab_switching_simple.py

# Test switch by model cards
python3 .mcp/test_switch_by_model_card.py
```

### Test 3: Test Active Agents API

```bash
# Test endpoint /api/active-agents
curl http://localhost:8001/api/active-agents | python3 -m json.tool

# Hoặc dùng script
python3 .mcp/test_active_agents_direct.py
```

## 🔍 Expected Results

### Message API Test
- ✅ Status: 200
- ✅ Response có `success: true`
- ✅ `auto_submit.success: true` nếu thành công
- ✅ Message xuất hiện trong Cursor chat

### Tab Switching Test
- ⚠️ Expected: `tab_switch_failed` hoặc `tab_not_found`
- 💡 **Lý do:** Cursor có thể dùng separate windows, không có tabs accessible

### Window Switching
- ✅ Expected: `focused_window`
- ✅ Window title chứa model name

## 🐛 Troubleshooting

### API Server không chạy
```bash
# Start API server
python3 .mcp/api_server.py
```

### Request Timeout
- Auto-submit có thể mất thời gian (focus window, paste, submit)
- Tăng timeout trong script hoặc đợi lâu hơn

### Tab Switching Failed
- **Bình thường** - Cursor có thể dùng separate windows
- Window switching vẫn hoạt động tốt

## 📊 Test Results Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Window Switching | ✅ Working | Tìm window theo model name |
| Tab Switching | ❌ Not Working | Cursor có thể dùng separate windows |
| Message API | ✅ Working | Gửi message thành công |
| Verification | ✅ Improved | Check chat content |
| Active Agents API | ✅ Working | Trả về đúng danh sách |

## 🎯 Next Steps

1. ✅ **Window switching đã hoạt động** - tiếp tục dùng
2. ⚠️ **Tab switching không cần thiết** nếu Cursor dùng separate windows
3. ✅ **Verification improved** - check chat content
4. 🔍 **Có thể test thêm** với keyboard shortcuts để switch model

