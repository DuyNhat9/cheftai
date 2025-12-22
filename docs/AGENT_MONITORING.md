# Agent Monitoring Guide

## 🎯 Tổng Quan

File này hướng dẫn cách monitor và quản lý 4 Agent đang làm việc song song.

---

## 📊 Trạng Thái Hiện Tại

### Agents Đang Làm Việc:

| Agent | Status | Current Task | Model |
|-------|--------|--------------|-------|
| **Backend_AI_Dev** | 🔄 Working | T009: Setup Firestore | GPT-5.1 Codex High Fast |
| **UI_UX_Dev** | 🔄 Working | T015: RecipeResultScreen | Opus 4.1 |
| **Testing_QA** | 🔄 Working | T017: Backend tests | o3 Pro |

### Tasks Đang IN_PROGRESS:

- **T009**: Backend Firestore setup (Backend_AI_Dev)
- **T015**: RecipeResultScreen migration (UI_UX_Dev)
- **T017**: FastAPI endpoint tests (Testing_QA)

---

## 🔍 Cách Monitor Agents

### 1. **Check Shared State**
```bash
# Đọc file để xem status
cat .mcp/shared_state.json | jq '.agents'
```

### 2. **Check Task Board**
```bash
# Xem tasks đang IN_PROGRESS
cat .mcp/shared_state.json | jq '.task_board[] | select(.status == "IN_PROGRESS")'
```

### 3. **Monitor trong Cursor**
- Xem từng chat window để biết Agent đang làm gì
- Check "0/5 To-Dos" để biết progress
- Xem status messages trong chat

---

## ⚠️ Lưu Ý Khi Agents Làm Việc Song Song

### 1. **Không Conflict Files**
- ✅ Mỗi Agent làm file riêng:
  - Backend_AI_Dev → `backend/`
  - UI_UX_Dev → `lib/presentation/`
  - Testing_QA → `backend/tests/`, `test/`

### 2. **Shared State Updates**
- ⚠️ Nhiều Agent có thể update `shared_state.json` cùng lúc
- ✅ Mỗi Agent nên:
  1. Đọc file trước
  2. Update task của mình
  3. Save ngay
  4. Tránh update tasks của Agent khác

### 3. **Dependencies**
- ✅ Check dependencies trước khi làm task
- ✅ Đợi dependency COMPLETED nếu cần

---

## 🔄 Hand-off Protocol

### Khi Agent Hoàn Thành Task:

**Backend_AI_Dev hoàn thành T009:**
```
1. Update shared_state.json:
   - T009 status → COMPLETED
   - Backend_AI_Dev status → Idle
   
2. Hand-off message:
   "Đã hoàn thành T009: Firestore setup.
   UI_UX_Dev có thể làm T011 (Setup Firebase) vì T010 đã COMPLETED."
```

**UI_UX_Dev hoàn thành T015:**
```
1. Update shared_state.json:
   - T015 status → COMPLETED
   - UI_UX_Dev status → Working (nếu còn task khác)
   
2. Hand-off message:
   "Đã hoàn thành T015: RecipeResultScreen.
   Testing_QA có thể làm T018 (Widget tests) vì T013, T014, T015 đã COMPLETED."
```

---

## 📋 Checklist Cho Mỗi Agent

### Trước Khi Bắt Đầu:
- [ ] Đọc `shared_state.json`
- [ ] Check task dependencies đã COMPLETED
- [ ] Update task status → IN_PROGRESS
- [ ] Update agent status → Working

### Trong Khi Làm Việc:
- [ ] Làm code trong folder riêng (không conflict)
- [ ] Không sửa files của Agent khác
- [ ] Cập nhật shared_memory nếu tạo constants mới

### Sau Khi Hoàn Thành:
- [ ] Update task status → COMPLETED
- [ ] Update agent status → Idle (hoặc Working nếu còn task)
- [ ] Ghi vào shared_memory.active_constants
- [ ] Hand-off cho Agent tiếp theo (nếu có)

---

## 🚨 Troubleshooting

### Vấn Đề: Agent bị stuck
**Giải pháp:**
1. Check chat window xem có error không
2. Đọc shared_state.json xem task status
3. Nếu cần, cancel và restart task

### Vấn Đề: Conflict trong shared_state.json
**Giải pháp:**
1. Đọc file trước khi update
2. Chỉ update tasks của mình
3. Save ngay sau khi update

### Vấn Đề: Agent không làm đúng task
**Giải pháp:**
1. Check prompt đã assign role đúng chưa
2. Remind Agent đọc shared_state.json
3. Clarify task requirements

---

## 💡 Tips

1. **Pin shared_state.json:**
   - Mở file trong editor
   - Pin để dễ theo dõi

2. **Regular Check-ins:**
   - Mỗi 10-15 phút check progress
   - Xem tasks nào đã COMPLETED
   - Trigger tasks tiếp theo nếu cần

3. **Communication:**
   - Mỗi Agent nên ghi hand-off message rõ ràng
   - Update shared_state.json ngay khi xong

---

**Last Updated:** 2025-12-17  
**Maintained by:** Agent Architect


