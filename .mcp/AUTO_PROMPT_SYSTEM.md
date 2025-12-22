# 🤖 Hệ Thống Auto-Prompt Cho Agents

## 🎯 Mục Đích

Dashboard tự động tạo prompt file cho từng agent. Agent chỉ cần đọc file này khi bắt đầu chat → Tự động nhận task và làm việc.

---

## 🔄 Cách Hoạt Động

### 1. Dashboard Trigger
```
User bấm "Trigger Agent" trong dashboard
    ↓
Dashboard tạo:
  - trigger_queue.json (trigger data)
  - pending_prompts/{AgentName}.md (prompt file)
```

### 2. Agent Nhận Prompt
```
Agent mở chat window
    ↓
Agent đọc: .mcp/pending_prompts/{AgentName}.md
    ↓
Agent tự động làm task theo prompt
    ↓
Agent xóa prompt file sau khi đọc
```

---

## 📋 Setup Agent (1 Lần)

Mỗi Agent cần paste prompt này vào chat window khi bắt đầu:

```
Bạn là Agent [TÊN_AGENT] cho dự án CheftAi Android.

🔴 BƯỚC 1 - ĐỌC PROMPT FILE (BẮT BUỘC):
1. Đọc file: .mcp/pending_prompts/[TÊN_AGENT].md
2. Nếu file tồn tại:
   ✅ Làm task ngay theo prompt trong file
   ✅ Xóa file sau khi đọc (hoặc update status)
   ✅ Update trigger_queue.json và shared_state.json

🟢 BƯỚC 2 - NẾU KHÔNG CÓ PROMPT FILE:
1. Đọc .mcp/trigger_queue.json
2. Tìm trigger có agent = "[TÊN_AGENT]" và status = "pending"
3. Nếu có → Làm task đó

🟡 BƯỚC 3 - NẾU KHÔNG CÓ TRIGGER:
1. Đọc .mcp/shared_state.json
2. Xem tasks của bạn (owner = "[TÊN_AGENT]")
3. Làm task PENDING đầu tiên

Bắt đầu: Đọc .mcp/pending_prompts/[TÊN_AGENT].md trước!
```

**Thay `[TÊN_AGENT]` bằng:**
- `Backend_AI_Dev`
- `UI_UX_Dev`
- `Testing_QA`
- `Architect`

---

## 📁 File Structure

```
.mcp/
├── trigger_queue.json          # Trigger data
├── pending_prompts/            # Prompt files cho từng agent
│   ├── Backend_AI_Dev.md
│   ├── UI_UX_Dev.md
│   ├── Testing_QA.md
│   └── Architect.md
└── shared_state.json           # Project state
```

---

## 🔧 API Endpoints

### GET `/api/prompt/{AgentName}`
Lấy prompt file cho agent

### POST `/api/clear-prompt/{AgentName}`
Xóa prompt file sau khi agent đọc

---

## ✅ Workflow Hoàn Chỉnh

```
1. Dashboard → Bấm "Trigger Agent"
   ↓
2. API Server tạo:
   - trigger_queue.json entry
   - pending_prompts/{Agent}.md
   ↓
3. Agent mở chat → Đọc pending_prompts/{Agent}.md
   ↓
4. Agent làm task theo prompt
   ↓
5. Agent update:
   - trigger_queue.json (status → completed)
   - shared_state.json (task → COMPLETED)
   - Xóa pending_prompts/{Agent}.md
```

---

## 💡 Lợi Ích

✅ **Tự động hoàn toàn:** Agent không cần copy/paste  
✅ **Dễ theo dõi:** Mỗi agent có file prompt riêng  
✅ **Không trùng lặp:** Prompt file tự xóa sau khi đọc  
✅ **Real-time:** Dashboard tạo prompt → Agent nhận ngay  

---

**Last Updated:** 2025-12-18

