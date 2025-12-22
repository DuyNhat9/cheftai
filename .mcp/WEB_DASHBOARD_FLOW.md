# 🔄 Flow Hoạt Động Của Web Dashboard

## 📋 Tổng Quan

Web dashboard cho phép gửi message tới các agent chat trong Cursor thông qua giao diện web, với khả năng tự động paste và submit vào chat đang mở.

---

## 🎯 Flow Chính: Gửi Message từ Web Dashboard

### **Bước 1: User Input (Frontend)**
```
User → Dashboard UI
├─ Chọn Agent từ dropdown (Architect, Backend_AI_Dev, UI_UX_Dev, Testing_QA)
├─ Nhập message vào textarea
└─ Click "📤 Send Message"
```

**File:** `.mcp/dashboard_enhanced.html` (hàm `sendMessageToAgent()`)

**Validation:**
- ✅ Kiểm tra agent đã được chọn (không phải "-- Chọn Agent --")
- ✅ Kiểm tra message không rỗng
- ✅ Disable button để tránh double submission

---

### **Bước 2: Auto Test & Fix (Frontend)**
```
Frontend → Health Check
├─ GET /api/state (kiểm tra API server đang chạy)
└─ Nếu fail → Warning nhưng vẫn tiếp tục
```

**Mục đích:** Đảm bảo API server đang chạy trước khi gửi request.

---

### **Bước 3: Gửi Request tới Backend (Frontend)**
```
Frontend → POST /api/messages
├─ Headers: Content-Type: application/json
├─ Body: {
│     agent: "Architect",
│     message: "User's message",
│     task_id: "ADHOC",
│     task_title: "Message from dashboard"
│   }
└─ Retry Logic: 3 attempts với exponential backoff
```

**File:** `.mcp/dashboard_enhanced.html` (lines 1193-1237)

**Retry Logic:**
- Attempt 1: Gửi ngay
- Attempt 2: Đợi 1s nếu attempt 1 fail
- Attempt 3: Đợi 2s nếu attempt 2 fail

---

### **Bước 4: Backend Xử Lý Request (API Server)**
```
API Server → /api/messages endpoint
├─ Parse request body
├─ Resolve chat_id từ agent name
│   └─ Tìm trong shared_state.json → agents[agent_name].worktree_id
├─ Tạo prompt file (.mcp/pending_prompts/{agent}.md)
│   └─ Format: Markdown với metadata (Agent, Chat ID, Task ID, Timestamp)
├─ Tạo trigger entry trong trigger_queue.json
├─ Gọi auto_submit_service.py
│   └─ python3 .mcp/auto_submit_service.py {agent} {prompt_file_path} [chat_id]
└─ Trả về response với auto_submit result
```

**File:** `.mcp/api_server.py` (path `/api/messages`)

**Response Structure:**
```json
{
  "success": true,
  "trigger_id": 1234567890,
  "prompt_file": "Architect.md",
  "chat_id": "qnu",
  "auto_submit": {
    "success": true,
    "skipped": false,
    "message": "[auto_submit_service]\n  agent = Architect\n  ...\n  ui_status = sent_to_cursor_ok"
  }
}
```

---

### **Bước 5: Auto-Submit Service (Python Script)**
```
auto_submit_service.py
├─ Nhận arguments: agent_name, prompt_file_path, [chat_id]
├─ Get agent worktree info từ shared_state.json
│   ├─ Tìm trong detected_chats (nếu có chat_id)
│   ├─ Tìm trong agents (nếu có agent_name)
│   └─ Fallback: Tìm trong worktree paths
├─ Resolve prompt text từ file
│   └─ Extract message sau "Yêu cầu từ dashboard web:"
├─ Find và focus Cursor window
│   ├─ Tìm window có chứa worktree_id/chat_id trong title
│   ├─ Fallback: Frontmost window
│   └─ Fallback: Window đầu tiên
│   └─ Nếu không có window → Activate Cursor app → Đợi 1s → Re-check
├─ Send message to Cursor
│   ├─ Copy message text vào clipboard
│   ├─ Focus vào Cursor window
│   ├─ Tìm và click vào chat input textarea
│   │   └─ Fallback: Tab key để focus
│   ├─ Paste (Cmd+V)
│   ├─ Đợi 1.0s để paste hoàn tất
│   ├─ Press Enter (key code 36)
│   └─ Đợi 0.8s để submit hoàn tất
└─ Return status: sent_to_cursor_ok | app_not_running | no_windows | ...
```

**File:** `.mcp/auto_submit_service.py`

**Key Functions:**
- `get_agent_worktree_info()`: Tìm worktree info từ shared_state.json
- `resolve_prompt_text()`: Extract message từ prompt file
- `find_and_focus_cursor_window()`: Tìm và focus Cursor window
- `send_to_cursor()`: Paste và submit message với retry logic (3 attempts)

---

### **Bước 6: Frontend Xử Lý Response**
```
Frontend nhận response từ /api/messages
├─ Parse JSON response
├─ Clear form (messageText.value = '')
├─ Verify prompt file
│   └─ GET /api/prompt/{agent} để kiểm tra file đã tạo
├─ Xử lý auto_submit result
│   ├─ Nếu skipped: Hiển thị warning (không phải macOS hoặc thiếu điều kiện)
│   ├─ Nếu success + sent_to_cursor_ok: Hiển thị success notification
│   ├─ Nếu success nhưng không sent_to_cursor_ok: Hiển thị warning
│   └─ Nếu failed + không skipped: Gọi retryAutoSubmit()
├─ Reload data (loadData()) sau 1s để đồng bộ UI
└─ Re-enable button
```

**File:** `.mcp/dashboard_enhanced.html` (lines 1239-1359)

**Notification Messages:**
- ✅ Success: "Message đã gửi tới {agent}! Message đã được paste và submit vào chat đang mở"
- ⚠️ Warning: "Prompt file đã tạo! Auto-submit bị skip. Vui lòng mở chat của {agent} và đọc prompt file."
- ❌ Error: "Gửi tin nhắn thất bại: {error.message}"

---

### **Bước 7: Retry Auto-Submit (Nếu Cần)**
```
retryAutoSubmit(agent, promptFile, chatId, maxRetries)
├─ Nếu auto_submit từ /api/messages failed và không skipped
├─ POST /api/auto-submit
│   └─ Body: { agent, chat_id, prompt_path }
├─ Retry logic: 2 attempts với exponential backoff
└─ Xử lý response tương tự như trên
```

**File:** `.mcp/dashboard_enhanced.html` (hàm `retryAutoSubmit()`)

**Mục đích:** Retry auto-submit nếu lần đầu từ `/api/messages` thất bại.

---

## 🔄 Flow Diagram

```
┌─────────────────┐
│   User Input    │
│  (Dashboard UI) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validation     │
│  (Agent, Msg)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Health Check    │
│ GET /api/state  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      Retry (3x)
│ POST /api/      │◄──────┐
│ messages        │       │
└────────┬────────┘       │
         │                │
         ▼                │
┌─────────────────┐       │
│ API Server      │       │
│ (api_server.py) │       │
└────────┬────────┘       │
         │                │
         ├─► Create prompt file
         ├─► Create trigger entry
         └─► Call auto_submit_service.py
                 │
                 ▼
         ┌─────────────────┐
         │ auto_submit_    │
         │ service.py      │
         └────────┬────────┘
                  │
                  ├─► Get worktree info
                  ├─► Find Cursor window
                  ├─► Focus window
                  ├─► Paste message
                  └─► Submit (Enter)
                          │
                          ▼
                  ┌─────────────────┐
                  │ Return status   │
                  │ (sent_to_cursor │
                  │  _ok | ...)     │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Response với    │
                  │ auto_submit     │
                  │ result          │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Frontend xử lý  │
                  │ response        │
                  └────────┬────────┘
                           │
                           ├─► Verify prompt file
                           ├─► Show notification
                           ├─► Reload data
                           └─► Re-enable button
```

---

## 🔑 Key Features

### **1. Retry Logic**
- **Frontend:** 3 attempts cho `/api/messages` với exponential backoff
- **Auto-submit:** 3 attempts cho `send_to_cursor()` với exponential backoff
- **Retry Auto-submit:** 2 attempts cho `/api/auto-submit` nếu cần

### **2. Error Handling**
- ✅ Health check trước khi gửi
- ✅ Validate input (agent, message)
- ✅ Parse JSON response với try-catch
- ✅ Verify prompt file sau khi gửi
- ✅ Disable button để tránh double submission
- ✅ Finally block để re-enable button

### **3. Auto-Submit Logic**
- ✅ Tự động tìm và focus Cursor window
- ✅ Tự động activate Cursor nếu không có window
- ✅ Tìm và click vào chat input textarea
- ✅ Fallback về Tab key nếu không tìm thấy textarea
- ✅ Paste và submit với delays để đảm bảo hoàn tất

### **4. Status Reporting**
- ✅ `sent_to_cursor_ok`: Message đã được paste và submit thành công
- ✅ `focused_window`: Đã focus vào Cursor nhưng chưa chắc đã submit
- ✅ `app_not_running`: Cursor không chạy
- ✅ `no_windows`: Cursor không có window nào
- ✅ `skipped`: Auto-submit bị skip (không phải macOS hoặc thiếu điều kiện)

---

## 📝 Files Liên Quan

1. **Frontend:** `.mcp/dashboard_enhanced.html`
   - Hàm `sendMessageToAgent()`: Gửi message
   - Hàm `retryAutoSubmit()`: Retry auto-submit
   - Hàm `checkApiServerStatus()`: Health check
   - Hàm `verifyPromptFile()`: Verify prompt file

2. **Backend:** `.mcp/api_server.py`
   - Endpoint `/api/messages`: Nhận request và tạo prompt file
   - Endpoint `/api/auto-submit`: Retry auto-submit
   - Endpoint `/api/prompt/{agent}`: Get prompt file để verify

3. **Auto-Submit Service:** `.mcp/auto_submit_service.py`
   - `get_agent_worktree_info()`: Tìm worktree info
   - `resolve_prompt_text()`: Extract message từ file
   - `find_and_focus_cursor_window()`: Tìm và focus window
   - `send_to_cursor()`: Paste và submit message

4. **State Files:**
   - `.mcp/shared_state.json`: Chứa agent mappings và detected chats
   - `.mcp/trigger_queue.json`: Chứa trigger entries
   - `.mcp/pending_prompts/{agent}.md`: Prompt files cho từng agent

---

## 🪟 Flow Mở Agent Window từ Web Dashboard

### **Bước 1: User Click "Open Window" (Frontend)**
```
User → Dashboard UI
├─ Click nút "🪟 Open Window" trên agent card
└─ Gọi hàm `openAgentWindow(agentName)`
```

**File:** `.mcp/dashboard_enhanced.html` (hàm `openAgentWindow()`)

---

### **Bước 2: Gửi Request tới Backend (Frontend)**
```
Frontend → POST /api/open-agent-window
├─ Headers: Content-Type: application/json
├─ Body: {
│     agent: "Architect"  // Tên agent
│   }
└─ Timeout: 10s
```

**File:** `.mcp/dashboard_enhanced.html` (line ~715)

---

### **Bước 3: Backend Xử Lý (API Server)**
```
API Server → POST /api/open-agent-window
├─ Đọc shared_state.json để lấy detected_chats
├─ Tìm chat tương ứng với agent_name
│   ├─ Ưu tiên: worktree_id (nếu có trong request)
│   └─ Fallback: chat đầu tiên của agent_name
├─ Gọi open_or_focus_agent_window() từ open_separate_windows.py
└─ Trả về JSON: { success: true/false, agent, worktree_id }
```

**File:** `.mcp/api_server.py` (line ~825)

**Helper Function:** `.mcp/open_separate_windows.py` → `open_or_focus_agent_window()`

**Logic:**
1. Tìm Cursor window hiện có theo `worktree_id` hoặc `model`
2. Nếu không tìm thấy → mở window mới bằng `cursor <worktree_path>`
3. Focus window và đảm bảo chat panel được mở

---

### **Bước 4: Hiển Thị Kết Quả (Frontend)**
```
Frontend → Hiển thị notification
├─ Success: "✅ Đã mở/focus window cho Architect (ghr)"
└─ Error: "❌ Không mở được window: <error message>"
```

**Error Handling:**
- API server không phản hồi → "Không thể kết nối đến API server"
- Agent không có chat đang mở → "No active chat window found"
- AppleScript lỗi → "Failed to open agent window: <error>"

---

## 🎯 Kết Luận

Flow hoạt động của web dashboard được thiết kế với:
- ✅ **Robustness:** Retry logic ở nhiều tầng
- ✅ **User Experience:** Clear notifications và error messages
- ✅ **Reliability:** Health checks và verification
- ✅ **Automation:** Tự động paste và submit vào Cursor chat

Hệ thống đảm bảo message được gửi thành công từ web dashboard tới Cursor chat với độ tin cậy cao.




