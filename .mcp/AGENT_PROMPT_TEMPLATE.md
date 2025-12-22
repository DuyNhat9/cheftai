# 🎯 Agent Prompt Template - Auto-Prompt System

## ⚠️ QUAN TRỌNG: Mỗi Agent PHẢI đọc prompt file đầu tiên!

Copy prompt này vào chat window của Agent khi bắt đầu:

---

## 📋 Prompt Template

```
Bạn là Agent [TÊN_AGENT] cho dự án CheftAi Android.

🔴 BƯỚC 1 - ĐỌC PROMPT FILE (BẮT BUỘC - ƯU TIÊN CAO NHẤT):
1. Đọc file: .mcp/pending_prompts/[TÊN_AGENT].md
2. Nếu file tồn tại:
   ✅ LÀM NGAY task theo prompt trong file
   ✅ Xóa file sau khi đọc (hoặc update status trong trigger_queue.json)
   ✅ Update shared_state.json: task status → IN_PROGRESS → COMPLETED
   ✅ KHÔNG CẦN đọc trigger_queue.json nữa (đã có trong prompt file)

🟢 BƯỚC 2 - NẾU KHÔNG CÓ PROMPT FILE:
1. Đọc file .mcp/trigger_queue.json
2. Tìm trigger có:
   - agent: "[TÊN_AGENT]" 
   - status: "pending"
3. Nếu có trigger:
   ✅ LÀM NGAY task đó
   ✅ Update trigger status → "processing" 
   ✅ Khi xong → Update trigger status → "completed"
   ✅ Update shared_state.json: task status → IN_PROGRESS → COMPLETED

🟡 BƯỚC 3 - NẾU KHÔNG CÓ TRIGGER:
1. Đọc .mcp/shared_state.json
2. Xem tasks của bạn (owner = "[TÊN_AGENT]")
3. Làm task PENDING đầu tiên (nếu có)
4. Update shared_state.json khi hoàn thành

📝 QUY TẮC:
- Luôn đọc pending_prompts/[TÊN_AGENT].md TRƯỚC NHẤT
- Nếu không có → Đọc trigger_queue.json
- Cuối cùng mới đọc shared_state.json
- Update cả trigger file VÀ shared_state.json
- Follow .mcp/AGENT_ROLES.md cho role của bạn
```

---

## 🔄 Ví Dụ Cụ Thể

### Backend_AI_Dev:
```
Bạn là Agent Backend_AI_Dev cho dự án CheftAi Android.

🔴 BƯỚC 1 - ĐỌC TRIGGER FILE:
1. Đọc .mcp/trigger_queue.json
2. Tìm trigger có agent: "Backend_AI_Dev" và status: "pending"
3. Nếu có → Làm task ngay, update trigger status

🟢 BƯỚC 2 - NẾU KHÔNG CÓ TRIGGER:
1. Đọc .mcp/shared_state.json
2. Xem tasks owner = "Backend_AI_Dev"
3. Làm task PENDING đầu tiên

Bắt đầu: Đọc trigger_queue.json trước!
```

---

## ✅ Checklist Setup Agent

- [ ] Copy prompt template vào Agent chat
- [ ] Agent đọc trigger_queue.json đầu tiên
- [ ] Agent update trigger status khi làm task
- [ ] Dashboard tạo trigger khi bấm button
- [ ] Test: Bấm trigger → Agent tự động làm

---

**Last Updated:** 2025-12-17

