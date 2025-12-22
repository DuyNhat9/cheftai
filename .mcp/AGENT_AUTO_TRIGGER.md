# Hệ Thống Auto-Trigger Cho Agents

## 🎯 Vấn Đề

Dashboard chỉ copy command vào clipboard, Agent không tự động làm việc.

## ✅ Giải Pháp: Trigger File System

### Cách Hoạt Động:

1. **Dashboard tạo trigger file:** `.mcp/trigger_queue.json`
2. **Agent đọc trigger file:** Mỗi Agent check file này khi bắt đầu
3. **Agent tự động làm task:** Nếu có trigger cho mình, tự động làm

---

## 📋 Cách Setup

### Bước 1: Agent Phải Đọc Trigger File

Mỗi Agent cần thêm vào prompt đầu tiên:

```
Bạn là Agent [Tên_Agent] cho dự án CheftAi Android.

1. ĐỌC TRƯỚC: .mcp/trigger_queue.json để xem có task nào được trigger cho bạn không
2. Nếu có trigger:
   - Làm task ngay lập tức
   - Update trigger status → processing
   - Khi xong → Update trigger status → completed
3. Nếu không có trigger:
   - Đọc .mcp/shared_state.json
   - Xem tasks của bạn
   - Đợi trigger hoặc làm task PENDING
```

### Bước 2: Dashboard Tạo Trigger

Khi bạn bấm "Trigger Agent" trong dashboard:
- Dashboard tạo entry trong `trigger_queue.json`
- Agent sẽ tự động đọc và làm việc

---

## 🔄 Workflow

```
Dashboard → Bấm Trigger → Tạo trigger_queue.json
    ↓
Agent đọc trigger_queue.json → Thấy task của mình
    ↓
Agent làm task → Update shared_state.json
    ↓
Agent update trigger status → completed
```

---

## 📝 Trigger File Format

```json
{
  "triggers": [
    {
      "id": 1234567890,
      "agent": "Backend_AI_Dev",
      "task_id": "T009",
      "task_title": "Setup Firestore",
      "command": "Bạn là Agent Backend_AI_Dev...",
      "created_at": "2025-12-17T11:00:00Z",
      "status": "pending"
    }
  ],
  "last_trigger_id": 1234567890
}
```

---

## 💡 Best Practice

1. **Agent check trigger file đầu tiên** khi bắt đầu chat
2. **Dashboard tạo trigger** khi user bấm button
3. **Agent xử lý trigger** và update status
4. **Cleanup:** Xóa trigger cũ sau khi completed

---

**Last Updated:** 2025-12-17

