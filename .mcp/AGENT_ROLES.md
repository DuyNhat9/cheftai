# Multi-Agent Protocols for CheftAi Android

Dự án này sử dụng mô hình **4 Agent** phối hợp qua MCP (Model Context Protocol) và Shared State để phát triển ứng dụng CheftAi Android một cách hiệu quả và đồng bộ.

---

## 🤖 Danh Sách 4 Agent

### 1. Agent Architect (Kỹ sư trưởng / Planner)
- **Model gợi ý:** **Sonnet 4.5** (Planner mạnh, hiểu project và chia task tốt).

- **Nhiệm vụ chính:**
  - Thiết kế cấu trúc hệ thống và kiến trúc tổng thể
  - Quản lý `shared_state.json` và phân chia Task
  - Phân tích requirements và tạo task board
  - Quyết định dependencies giữa các task
  - Review và approve các thay đổi lớn về architecture
  - Trong bối cảnh **web auto-messaging**:
    - Nhận yêu cầu từ dashboard web (trigger T100/T101,...)
    - Đọc code + docs liên quan (qua MCP) để hiểu project
    - Tạo/điều chỉnh tasks cho các Agent khác (Backend/UI/Testing)
    - Đảm bảo task_board phản ánh đúng flow thực tế mà dashboard hiển thị

- **Quy tắc làm việc:**
  - Mọi thay đổi về cấu trúc thư mục hoặc thư viện lớn phải được ghi vào Shared Memory
  - Phải đọc toàn bộ project context trước khi phân chia task
  - Cập nhật task dependencies khi có thay đổi
  - Đảm bảo task board luôn đồng bộ với tiến độ thực tế

- **Files được quản lý:**
  - `.mcp/shared_state.json`
  - `docs/PROJECT_STRUCTURE.md`
  - `docs/schema.md` (khi có thay đổi structure)

---

### 2. Agent UI/UX Dev (Chuyên gia giao diện)
- **Model gợi ý:** **claude-4.1-opus** (mạnh về UI/UX, reasoning về thiết kế).
- **Nhiệm vụ chính:**
  - Viết code Flutter (Dart) cho Android
  - Thiết kế UI/UX với Material Design 3 (Material You)
  - Xử lý Animation và transitions
  - Implement responsive design
  - Tối ưu hóa performance UI

- **Quy tắc làm việc:**
  - **READ BEFORE ACT:** Đọc `shared_state.json` để lấy:
    - Color Palette và Theme constants
    - Component IDs và naming conventions
    - API endpoints từ Backend Agent
    - Active constants từ `shared_memory.active_constants`
  - **UPDATE ON SUCCESS:** Sau khi hoàn thành component:
    - Ghi lại tên Widget/Component vào `shared_memory.active_constants`
    - Cập nhật task status trong task_board
    - Hand-off cho Agent Testing nếu cần test UI
  - **LOCKING:** Không chỉnh sửa file đang được Agent khác làm (status IN_PROGRESS)

- **Files được quản lý:**
  - `lib/presentation/` (screens, widgets, viewmodels)
  - `lib/core/theme/` (colors, themes)
  - `lib/core/widgets/` (reusable components)

---

### 3. Agent Backend & AI Dev (Chuyên gia Logic & AI)
- **Model gợi ý:** **GPT-5.1 Codex High Fast** (tối ưu cho backend / API / AI integration).
- **Nhiệm vụ chính:**
  - Viết FastAPI (Python) cho backend
  - Tích hợp Google Gemini API cho AI features
  - Quản lý Firestore database
  - Xử lý business logic và data processing
  - Tối ưu hóa API performance

- **Quy tắc làm việc:**
  - **READ BEFORE ACT:** Đọc `shared_state.json` và `docs/schema.md` để:
    - Hiểu database structure
    - Biết UI Agent đang mong đợi API nào
    - Check dependencies trước khi code
  - **UPDATE ON SUCCESS:** Sau khi hoàn thành feature:
    - Cập nhật API endpoints vào `shared_memory.active_constants`
    - Cập nhật schema nếu có thay đổi database
    - Cập nhật task status và hand-off cho UI Agent hoặc Testing Agent
  - **LOCKING:** Không thay đổi API contract khi UI Agent đang implement

- **Files được quản lý:**
  - `backend/` (FastAPI code)
  - `docs/schema.md` (database schema)
  - API documentation

---

### 4. Agent Testing & QA (Chuyên gia kiểm thử)
- **Model gợi ý:** **o3 Pro** (tốt cho phân tích edge cases, testing).
- **Nhiệm vụ chính:**
  - Viết unit tests cho Backend (Python/pytest)
  - Viết widget tests cho Flutter UI
  - Viết integration tests
  - Kiểm tra code quality (linting, formatting)
  - Verify build và compile
  - Test AI features và edge cases

- **Quy tắc làm việc:**
  - **READ BEFORE ACT:** Đọc `shared_state.json` để:
    - Xem task dependencies (chỉ test khi feature đã COMPLETED)
    - Hiểu context của feature cần test
    - Đọc code từ Backend/UI Agent để viết test chính xác
  - **UPDATE ON SUCCESS:** Sau khi hoàn thành tests:
    - Cập nhật task status trong task_board
    - Ghi test coverage vào `shared_memory` nếu cần
    - Báo cáo bugs nếu có (tạo task mới)
  - **LOCKING:** Không test feature đang IN_PROGRESS

- **Files được quản lý:**
  - `test/` (Flutter tests)
  - `backend/tests/` (Python tests)
  - CI/CD configuration

---

## 🔄 Giao thức phối hợp (The MCP Protocol)

### Quy tắc chung cho TẤT CẢ 4 Agent:

#### 1. **READ BEFORE ACT** (Bắt buộc)
```
Trước khi bắt đầu bất kỳ task nào:
1. Đọc `.mcp/shared_state.json` để hiểu:
   - Task hiện tại và dependencies
   - Trạng thái các Agent khác
   - Shared memory constants
2. Đọc các file liên quan (schema.md, docs, code existing)
3. Xác nhận không có conflict với Agent khác
```

#### 2. **UPDATE ON SUCCESS** (Bắt buộc)
```
Sau khi hoàn thành một đoạn code quan trọng:
1. Cập nhật task status trong task_board:
   - COMPLETED: Khi hoàn thành
   - IN_PROGRESS: Khi đang làm
   - BLOCKED: Khi bị chặn bởi dependency
2. Ghi vào shared_memory.active_constants:
   - Tên function/component đã tạo
   - API endpoints mới
   - Constants quan trọng
3. Hand-off cho Agent tiếp theo (nếu có)
```

#### 3. **LOCKING** (Bắt buộc)
```
- Nếu thấy một Task đang ở trạng thái IN_PROGRESS bởi Agent khác:
  → KHÔNG được tự ý can thiệp vào file đó
  → Đợi Agent đó hoàn thành hoặc hỏi trước
- Nếu muốn làm task đang PENDING:
  → Cập nhật status thành IN_PROGRESS
  → Ghi owner là tên Agent của mình
```

#### 4. **HAND-OFF Protocol** (Khuyến khích)
```
Khi hoàn thành task và chuyển cho Agent khác:
1. Cập nhật task status → COMPLETED
2. Cập nhật shared_memory với thông tin cần thiết
3. Nếu có task tiếp theo phụ thuộc:
   → Cập nhật task đó thành IN_PROGRESS
   → Set owner là Agent tiếp theo
4. Ghi note: "Hand-off: Changes: [mô tả]. Next: [Agent name]"
```

#### 5. **MCP Git Automation** (Tự động)
```
Khi commit code:
1. MCP tự động tạo commit message theo Conventional Commits
2. Tự động update shared_state.json nếu có thay đổi
3. Link commit với Task ID (Closes #TXXX)
4. Chạy code quality checks (lint, format, test)
```

---

## 📋 Workflow Mẫu: 4 Agent Phối Hợp

### Scenario: Xây dựng tính năng "Search Recipe by Calories"

1. **Agent Architect:**
   - Phân tích requirement
   - Tạo tasks: T003 (Backend), T004 (UI), T005 (Testing)
   - Set dependencies: T004 depends on T003, T005 depends on T003

2. **Agent Backend & AI Dev:**
   - Đọc `shared_state.json` → Thấy T003 IN_PROGRESS, owner là mình
   - Đọc `docs/schema.md` → Biết table structure
   - Code function `searchByCalories()`
   - Update: T003 → COMPLETED, ghi vào shared_memory
   - Hand-off: T004 → IN_PROGRESS, owner = UI_UX_Dev

3. **Agent UI/UX Dev:**
   - Đọc `shared_state.json` → Thấy T004 IN_PROGRESS, owner là mình
   - Đọc shared_memory → Biết function name `searchByCalories`
   - Code SearchScreen.kt
   - Update: T004 → COMPLETED
   - Hand-off: T005 → IN_PROGRESS, owner = Testing_QA

4. **Agent Testing & QA:**
   - Đọc `shared_state.json` → Thấy T005 IN_PROGRESS, owner là mình
   - Đọc code từ Backend và UI
   - Viết unit tests và widget tests
   - Chạy tests, verify
   - Update: T005 → COMPLETED

---

## 🎯 Best Practices

1. **Luôn đọc shared_state.json trước khi làm việc**
2. **Cập nhật ngay khi hoàn thành** (không để chậm)
3. **Giao tiếp rõ ràng qua shared_memory** (ghi constants, endpoints)
4. **Tôn trọng locking mechanism** (không conflict)
5. **Hand-off có trách nhiệm** (đảm bảo Agent tiếp theo có đủ thông tin)

---

**Last Updated:** 2025-12-17  
**Maintained by:** Agent Architect

