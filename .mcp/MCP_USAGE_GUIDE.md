# Hướng Dẫn Sử Dụng MCP Cho 4 Agent

## 📖 Tổng Quan

File này hướng dẫn cách 4 Agent sử dụng MCP (Model Context Protocol) để phối hợp làm việc hiệu quả trong dự án CheftAi Android.

---

## 🔧 Các MCP Tools Có Sẵn

### 1. MCP Filesystem
- **Mục đích:** Đọc/ghi files trong project
- **Khi nào dùng:** 
  - Đọc `shared_state.json` trước khi làm việc
  - Đọc code từ Agent khác
  - Đọc schema, docs, config files

### 2. MCP Terminal
- **Mục đích:** Chạy commands (build, test, lint)
- **Khi nào dùng:**
  - Chạy tests: `flutter test` hoặc `pytest`
  - Check code quality: `dart analyze`, `dart format`
  - Build project: `flutter build apk`

### 3. MCP Git (nếu có)
- **Mục đích:** Tự động hóa Git workflow
- **Khi nào dùng:**
  - Commit code sau khi hoàn thành task
  - Tạo commit message tự động
  - Update shared_state.json và commit cùng lúc

---

## 📋 Quy Trình Làm Việc Cho Từng Agent

### 🤖 Agent Architect

#### Bước 1: Đọc Context
```bash
# Dùng MCP Filesystem đọc:
- .mcp/shared_state.json (xem task board hiện tại)
- docs/PROJECT_STRUCTURE.md (hiểu cấu trúc)
- README.md (hiểu tổng quan project)
```

#### Bước 2: Phân Tích & Tạo Task
```json
// Cập nhật shared_state.json:
{
  "task_board": [
    {
      "id": "TXXX",
      "title": "...",
      "owner": "Agent_Name",
      "status": "PENDING",
      "dependency": "TYYY",  // Nếu có
      "description": "..."
    }
  ]
}
```

#### Bước 3: Hand-off
- Set task status: `IN_PROGRESS`
- Set owner: Tên Agent sẽ làm
- Ghi note vào description

---

### 🎨 Agent UI/UX Dev

#### Bước 1: Đọc Shared State (BẮT BUỘC)
```bash
# Dùng MCP Filesystem đọc .mcp/shared_state.json
# Lấy thông tin:
- Task đang IN_PROGRESS, owner là mình
- Dependencies đã COMPLETED chưa
- shared_memory.active_constants (API endpoints, constants)
- shared_memory.ui_theme (color palette)
```

#### Bước 2: Đọc Code Backend (nếu cần)
```bash
# Nếu cần kết nối với Backend:
# Đọc backend code để biết API interface
# Hoặc đọc docs/schema.md để hiểu data structure
```

#### Bước 3: Code Flutter
```dart
// Viết code Flutter
// Sử dụng constants từ shared_memory
```

#### Bước 4: Update Shared State
```json
// Cập nhật shared_state.json:
{
  "shared_memory": {
    "active_constants": {
      "ui_component": "SearchScreen.kt",
      "widget_name": "RecipeCard"
    }
  },
  "task_board": [
    {
      "id": "T004",
      "status": "COMPLETED"  // Đã xong
    }
  ]
}
```

#### Bước 5: Hand-off cho Testing
```json
// Nếu có task testing:
{
  "id": "T005",
  "status": "IN_PROGRESS",
  "owner": "Testing_QA"
}
```

---

### ⚙️ Agent Backend & AI Dev

#### Bước 1: Đọc Shared State (BẮT BUỘC)
```bash
# Đọc .mcp/shared_state.json
# Kiểm tra:
- Task dependencies đã COMPLETED chưa
- shared_memory.tech_stack (biết dùng FastAPI, Gemini)
- docs/schema.md (database structure)
```

#### Bước 2: Code Backend
```python
# Viết FastAPI code
# Tích hợp Gemini API
# Quản lý Firestore
```

#### Bước 3: Update Shared State
```json
// Ghi API endpoints vào shared_memory:
{
  "shared_memory": {
    "active_constants": {
      "api_endpoint": "/api/recipes/search",
      "function_name": "searchByCalories",
      "request_params": ["minCal", "maxCal"]
    }
  }
}
```

#### Bước 4: Update Schema (nếu có thay đổi DB)
```markdown
# Cập nhật docs/schema.md nếu thay đổi database structure
```

#### Bước 5: Hand-off
- Task status → COMPLETED
- Hand-off cho UI Agent hoặc Testing Agent

---

### 🧪 Agent Testing & QA

#### Bước 1: Đọc Shared State (BẮT BUỘC)
```bash
# Đọc .mcp/shared_state.json
# Kiểm tra:
- Task dependencies đã COMPLETED
- shared_memory.active_constants (biết function/component cần test)
```

#### Bước 2: Đọc Code Cần Test
```bash
# Đọc code từ Backend Agent hoặc UI Agent
# Hiểu rõ implementation để viết test chính xác
```

#### Bước 3: Viết Tests
```dart
// Flutter widget tests
// Hoặc
```
```python
# Python unit tests với pytest
```

#### Bước 4: Chạy Tests (dùng MCP Terminal)
```bash
# Flutter:
flutter test

# Python:
pytest backend/tests/
```

#### Bước 5: Update Shared State
```json
{
  "task_board": [
    {
      "id": "T005",
      "status": "COMPLETED"
    }
  ],
  "shared_memory": {
    "test_coverage": "85%",  // Nếu có
    "last_build_status": "All tests passed"
  }
}
```

---

## 🔒 Locking Mechanism

### Quy Tắc:
1. **KHÔNG** chỉnh sửa file đang được Agent khác làm (status IN_PROGRESS)
2. **ĐỢI** Agent đó hoàn thành hoặc **HỎI** trước nếu cần thiết
3. **CẬP NHẬT** status thành IN_PROGRESS ngay khi bắt đầu làm task

### Ví Dụ:
```json
// ❌ SAI: Agent UI tự ý sửa file Backend đang IN_PROGRESS
{
  "id": "T003",
  "status": "IN_PROGRESS",
  "owner": "Backend_AI_Dev"  // Agent khác đang làm
}

// ✅ ĐÚNG: Agent UI đợi Backend hoàn thành
// Hoặc làm task khác không conflict
```

---

## 🔄 Hand-off Protocol

### Khi Hoàn Thành Task:

1. **Cập nhật Task Status:**
```json
{
  "id": "TXXX",
  "status": "COMPLETED"
}
```

2. **Ghi vào Shared Memory:**
```json
{
  "shared_memory": {
    "active_constants": {
      "your_component": "ComponentName",
      "your_function": "functionName"
    }
  }
}
```

3. **Hand-off Task Tiếp Theo:**
```json
{
  "id": "TYYY",
  "status": "IN_PROGRESS",
  "owner": "Next_Agent_Name"
}
```

4. **Ghi Note (khuyến khích):**
```
Hand-off: Changes: [Mô tả ngắn gọn]. Next: [Agent name]
```

---

## 🚀 MCP Git Automation

### Tự Động Commit Sau Khi Hoàn Thành:

1. **MCP tự động:**
   - Phân tích files đã thay đổi
   - Tạo commit message theo Conventional Commits
   - Link với Task ID: `Closes #TXXX`
   - Update shared_state.json và commit cùng lúc

2. **Ví dụ Commit Message:**
```
feat(ui): Add SearchScreen with Material Design 3

- Implement searchByCalories integration
- Add RecipeCard widget
- Connect to RecipeViewModel

Closes #T004
```

3. **Code Quality Checks:**
   - Tự động chạy `dart analyze` (Flutter)
   - Tự động chạy `pytest` (Backend)
   - Báo lỗi nếu có

---

## 📝 Checklist Cho Mỗi Agent

### Trước Khi Bắt Đầu:
- [ ] Đọc `.mcp/shared_state.json`
- [ ] Kiểm tra task dependencies đã COMPLETED
- [ ] Đọc code/docs liên quan
- [ ] Xác nhận không có conflict với Agent khác

### Trong Khi Làm Việc:
- [ ] Cập nhật task status → IN_PROGRESS
- [ ] Ghi owner là tên Agent của mình
- [ ] Code theo đúng standards và conventions

### Sau Khi Hoàn Thành:
- [ ] Cập nhật task status → COMPLETED
- [ ] Ghi vào shared_memory.active_constants
- [ ] Hand-off cho Agent tiếp theo (nếu có)
- [ ] Commit code (hoặc để MCP tự động)

---

## 🎯 Best Practices

1. **Luôn đọc shared_state.json TRƯỚC** khi làm bất cứ gì
2. **Cập nhật ngay** khi hoàn thành (không để chậm)
3. **Giao tiếp rõ ràng** qua shared_memory (ghi constants, endpoints)
4. **Tôn trọng locking** (không conflict)
5. **Hand-off có trách nhiệm** (đảm bảo Agent tiếp theo có đủ thông tin)

---

## ❓ Troubleshooting

### Vấn Đề: Không biết Agent nào đang làm task
**Giải pháp:** Đọc `shared_state.json` → Xem `task_board` → Check `owner` và `status`

### Vấn Đề: Không biết API endpoint từ Backend
**Giải pháp:** Đọc `shared_memory.active_constants` trong `shared_state.json`

### Vấn Đề: Task bị BLOCKED
**Giải pháp:** Check `dependency` trong task → Đợi task dependency COMPLETED

### Vấn Đề: Conflict với Agent khác
**Giải pháp:** 
1. Đọc shared_state.json để xem Agent nào đang làm
2. Đợi Agent đó hoàn thành
3. Hoặc hỏi trước nếu cần thiết

---

**Last Updated:** 2025-12-17  
**Maintained by:** Agent Architect

