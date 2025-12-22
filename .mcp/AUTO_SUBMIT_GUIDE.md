# Auto-Submit Guide - Gửi Message Tới Agent từ Dashboard

## ✅ Đã Hoạt Động

1. **API Endpoint**: `/api/messages` - Tạo prompt file và trigger
2. **Auto-Submit Service**: Gửi message vào Cursor chat đang active
3. **Dashboard UI**: Form "Send Message to Agent"

## 🔄 Cách Hoạt Động

### Flow:
```
Dashboard → POST /api/messages
  ↓
1. Tạo prompt file: .mcp/pending_prompts/{Agent}.md
2. Thêm vào trigger_queue.json
3. Gọi auto-submit service
  ↓
Auto-submit Service:
  - Copy prompt vào clipboard
  - Activate Cursor
  - Paste vào chat đang active
  - Gửi message (Enter)
```

## ⚠️ Lưu Ý Quan Trọng

### Auto-Submit Chỉ Gửi Vào Chat Đang Active

**Vấn đề**: Auto-submit chỉ có thể gửi vào Cursor window/chat đang active (focus). Nó **KHÔNG THỂ** tự động switch giữa các chat windows.

**Giải pháp**:
1. **Trước khi gửi message từ dashboard:**
   - Mở Cursor
   - Switch sang đúng chat của agent bạn muốn gửi message
   - Focus vào ô input của chat đó
   - Sau đó mới click "Send Message" trên dashboard

2. **Hoặc đọc prompt file manually:**
   - Prompt file được tạo tại: `.mcp/pending_prompts/{Agent}.md`
   - Agent có thể đọc trực tiếp từ file này
   - Hoặc copy nội dung và paste vào chat

## 🧪 Test Auto-Submit

### Test Manual:
```bash
python3 .mcp/auto_submit_service.py "Architect" "/Users/davidtran/Documents/cheftAi/.mcp/pending_prompts/Architect.md"
```

**Expected output:**
```
[auto_submit_service]
  agent       = Architect
  model       = Opus 4.1
  prompt_src  = file:/Users/.../Architect.md
  prompt_prev = # 🚀 Message từ Web Dashboard...
  ui_status   = sent_to_cursor_ok
```

### Test từ Dashboard:
1. Mở Cursor và switch sang chat của agent (ví dụ: Architect)
2. Focus vào ô input của chat
3. Mở dashboard: `http://localhost:8000/.mcp/dashboard_enhanced.html`
4. Vào tab "Trigger Agent" → "Send Message to Agent"
5. Chọn agent và nhập message
6. Click "Send Message"
7. Message sẽ được paste và gửi tự động vào chat đang active

## 🐛 Troubleshooting

### Auto-Submit Không Hoạt Động

**Nguyên nhân có thể:**
1. **Cursor không đang mở** → Mở Cursor trước
2. **Không có quyền Accessibility** → System Preferences → Security & Privacy → Accessibility → Thêm Cursor
3. **Không focus vào đúng chat** → Switch sang đúng chat trước khi gửi
4. **File path không đúng** → Kiểm tra prompt file có tồn tại không

**Kiểm tra:**
```bash
# Kiểm tra prompt file
ls -la .mcp/pending_prompts/

# Test auto-submit manual
python3 .mcp/auto_submit_service.py "Architect" ".mcp/pending_prompts/Architect.md"
```

### Fallback Options

Nếu auto-submit không hoạt động, agent vẫn có thể nhận message từ:
1. **Prompt file**: `.mcp/pending_prompts/{Agent}.md`
2. **Trigger queue**: `.mcp/trigger_queue.json`
3. **Shared state**: `.mcp/shared_state.json` (agents block)

## 💡 Best Practices

1. **Luôn switch sang đúng chat trước khi gửi**
2. **Kiểm tra prompt file đã được tạo** sau khi gửi
3. **Monitor trigger queue** để track messages
4. **Sử dụng fallback** nếu auto-submit fail

## 🔮 Future Improvements

1. **Auto-detect và switch chat**: Detect worktree và switch sang đúng chat window
2. **Notification system**: Thông báo khi agent nhận message
3. **Message status tracking**: Track sent/read/processed status
4. **Multi-chat support**: Gửi cùng lúc tới nhiều agents






