# Cách Hệ Thống Multi-Agent Hoạt Động Trong Cursor

## 🤔 Câu Hỏi: Tại Sao Chỉ Có Một Chat Làm Việc?

### Giải Thích Ngắn Gọn

**Trong Cursor, mỗi chat window = một Agent instance.** Các Agent không tự động làm việc song song. Bạn cần:

1. **Mở nhiều chat windows** (mỗi window = 1 Agent)
2. **Assign role cho từng chat** (bằng prompt)
3. **Trigger từng Agent** để làm task của họ

---

## 🎯 Cách Hoạt Động Thực Tế

### Scenario 1: Một Chat Window (Hiện Tại)

```
Chat Window 1 (Agent Architect)
├── Đọc shared_state.json
├── Tạo tasks
├── Làm code cho nhiều Agent
└── Cập nhật shared_state.json
```

**Vấn đề:** Một Agent đang làm việc của nhiều Agent khác → Không phải Multi-Agent thực sự

---

### Scenario 2: Multi-Agent Thực Sự (Khuyến Nghị)

```
Chat Window 1 (Agent Architect)
├── Đọc shared_state.json
├── Tạo tasks T006-T018
├── Cập nhật shared_state.json
└── Hand-off: "Backend_AI_Dev, làm task T009"

Chat Window 2 (Agent Backend_AI_Dev)
├── Đọc shared_state.json
├── Thấy T009 IN_PROGRESS, owner là mình
├── Làm code FastAPI
├── Cập nhật shared_state.json
└── Hand-off: "UI_UX_Dev, làm task T015"

Chat Window 3 (Agent UI_UX_Dev)
├── Đọc shared_state.json
├── Thấy T015 IN_PROGRESS, owner là mình
├── Làm code Flutter
└── Cập nhật shared_state.json

Chat Window 4 (Agent Testing_QA)
├── Đọc shared_state.json
├── Thấy T017-T018 PENDING
├── Đợi dependencies COMPLETED
└── Viết tests khi sẵn sàng
```

---

## 🚀 Cách Setup Multi-Agent Trong Cursor

### Bước 1: Mở Nhiều Chat Windows

1. **Mở Chat Window 1:**
   - Click vào chat icon hoặc `Cmd/Ctrl + L`
   - Đây sẽ là **Agent Architect**

2. **Mở Chat Window 2:**
   - Click vào chat icon lần nữa (hoặc tạo tab mới)
   - Đây sẽ là **Agent Backend_AI_Dev**

3. **Mở Chat Window 3:**
   - Tạo chat window thứ 3
   - Đây sẽ là **Agent UI_UX_Dev**

4. **Mở Chat Window 4:**
   - Tạo chat window thứ 4
   - Đây sẽ là **Agent Testing_QA**

---

### Bước 2: Assign Role Cho Từng Chat

#### Chat Window 1 - Agent Architect:
```
Prompt: "Bạn là Agent Architect. Đọc shared_state.json và xem task board. 
Tạo tasks mới nếu cần, hoặc review progress."
```

#### Chat Window 2 - Agent Backend_AI_Dev:
```
Prompt: "Bạn là Agent Backend_AI_Dev. Đọc shared_state.json. 
Làm task T009: Setup Firestore connection. 
Đọc docs/schema.md để hiểu database structure."
```

#### Chat Window 3 - Agent UI_UX_Dev:
```
Prompt: "Bạn là Agent UI_UX_Dev. Đọc shared_state.json. 
Làm task T015: Migrate RecipeResultScreen từ React. 
Reference: chefai/components/RecipeResult.tsx"
```

#### Chat Window 4 - Agent Testing_QA:
```
Prompt: "Bạn là Agent Testing_QA. Đọc shared_state.json. 
Kiểm tra tasks nào đã COMPLETED và cần tests. 
Viết tests cho T008 (FastAPI endpoint)."
```

---

### Bước 3: Hand-off Protocol

Khi một Agent hoàn thành task:

**Agent Backend_AI_Dev (trong Chat Window 2):**
```
"Đã hoàn thành T009. Cập nhật shared_state.json: T009 → COMPLETED.
Hand-off: UI_UX_Dev có thể làm T011 (Setup Firebase) vì dependency T010 đã COMPLETED."
```

**Agent UI_UX_Dev (trong Chat Window 3) sẽ:**
1. Đọc `shared_state.json` → Thấy T011 có thể làm
2. Cập nhật T011 → IN_PROGRESS, owner = UI_UX_Dev
3. Làm code
4. Cập nhật T011 → COMPLETED

---

## ⚠️ Vấn Đề Hiện Tại

### Tại Sao Chỉ Có Một Chat Làm Việc?

**Lý do:**
1. ✅ Bạn chỉ mở 1 chat window
2. ✅ Một Agent (Architect) đang làm việc của tất cả Agent khác
3. ✅ Các Agent khác chưa được "wake up" trong chat windows riêng

**Điều này KHÔNG SAI**, nhưng không phải Multi-Agent thực sự.

---

## ✅ Giải Pháp: Setup Multi-Agent Đúng Cách

### Option 1: Manual Multi-Agent (Khuyến Nghị)

1. **Mở 4 chat windows**
2. **Assign role cho từng window** (bằng prompt)
3. **Mỗi Agent đọc shared_state.json** trước khi làm việc
4. **Hand-off** khi hoàn thành task

**Ưu điểm:**
- ✅ Thực sự Multi-Agent
- ✅ Mỗi Agent focus vào chuyên môn
- ✅ Dễ track progress

**Nhược điểm:**
- ⚠️ Cần quản lý nhiều chat windows
- ⚠️ Cần nhớ hand-off

---

### Option 2: Sequential Agent (Hiện Tại)

1. **Một chat window**
2. **Một Agent làm tất cả** (nhưng đóng vai các Agent khác)
3. **Cập nhật shared_state.json** sau mỗi task

**Ưu điểm:**
- ✅ Đơn giản, không cần nhiều windows
- ✅ Nhanh cho MVP

**Nhược điểm:**
- ⚠️ Không phải Multi-Agent thực sự
- ⚠️ Một Agent phải biết tất cả domains

---

## 🎯 Best Practice

### Cho Dự Án Nhỏ (MVP):
- ✅ **Option 2** (Sequential) - Đủ dùng
- ✅ Một Agent làm tất cả, nhưng tuân thủ MCP Protocol
- ✅ Cập nhật shared_state.json đầy đủ

### Cho Dự Án Lớn (Production):
- ✅ **Option 1** (Multi-Agent) - Khuyến nghị
- ✅ 4 chat windows, mỗi Agent focus chuyên môn
- ✅ Hand-off protocol rõ ràng

---

## 📋 Checklist Để Setup Multi-Agent

- [ ] Mở 4 chat windows trong Cursor
- [ ] Assign role cho từng window (bằng prompt)
- [ ] Mỗi Agent đọc `shared_state.json` trước khi làm việc
- [ ] Tuân thủ MCP Protocol: READ BEFORE ACT, UPDATE ON SUCCESS
- [ ] Hand-off khi hoàn thành task
- [ ] Không conflict với Agent khác (check IN_PROGRESS)

---

## 💡 Tips

1. **Đặt tên chat windows:**
   - "Agent Architect"
   - "Agent Backend"
   - "Agent UI"
   - "Agent Testing"

2. **Pin shared_state.json:**
   - Mở file trong editor
   - Pin để dễ theo dõi

3. **Sử dụng Auto-Approved Transitions:**
   - Đã cấu hình trong Cursor Settings
   - Hand-off tự động approve

---

## 🔄 Workflow Mẫu

### Step 1: Architect Tạo Tasks
```
Chat Window 1 (Architect):
"Đọc shared_state.json. Tạo task T019: Add image picker feature."
```

### Step 2: Backend_AI_Dev Nhận Task
```
Chat Window 2 (Backend):
"Đọc shared_state.json. Thấy T019 PENDING. 
Làm task này: Add image upload endpoint."
```

### Step 3: UI_UX_Dev Nhận Task
```
Chat Window 3 (UI):
"Đọc shared_state.json. Thấy T020 (UI image picker) PENDING.
Làm task này: Add image picker widget."
```

### Step 4: Testing_QA Test
```
Chat Window 4 (Testing):
"Đọc shared_state.json. Thấy T019, T020 COMPLETED.
Viết tests cho image picker feature."
```

---

## ❓ FAQ

### Q: Có thể tự động hóa không?
**A:** Hiện tại Cursor chưa hỗ trợ auto-trigger Agent. Cần manual hand-off.

### Q: Có cần 4 chat windows không?
**A:** Không bắt buộc. Có thể dùng 1-2 windows và switch role.

### Q: Làm sao biết Agent nào đang làm gì?
**A:** Đọc `shared_state.json` → Xem `task_board` và `agents.status`.

---

**Last Updated:** 2025-12-17  
**Maintained by:** Agent Architect

