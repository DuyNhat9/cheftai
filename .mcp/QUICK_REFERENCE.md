# Quick Reference - 4 Agent System

## 🚀 Bắt Đầu Nhanh

### Bước 1: Đọc Shared State (BẮT BUỘC)
```bash
# Dùng MCP Filesystem đọc:
.mcp/shared_state.json
```

### Bước 2: Xác Định Vai Trò
- **Architect?** → Quản lý task board, phân chia công việc
- **UI_UX_Dev?** → Code Flutter, Material Design 3
- **Backend_AI_Dev?** → Code FastAPI, Gemini API
- **Testing_QA?** → Viết tests, check quality

### Bước 3: Làm Việc Theo Protocol
1. READ BEFORE ACT
2. UPDATE ON SUCCESS
3. LOCKING (không conflict)

---

## 📋 4 Agent Overview

| Agent | Vai Trò | Files Quản Lý | Status Hiện Tại |
|-------|---------|---------------|-----------------|
| **Architect** | Kỹ sư trưởng | `.mcp/shared_state.json`, `docs/` | Working (T002) |
| **UI_UX_Dev** | Giao diện | `lib/presentation/`, `lib/core/theme/` | Idle |
| **Backend_AI_Dev** | Logic & AI | `backend/`, `docs/schema.md` | Idle |
| **Testing_QA** | Kiểm thử | `test/`, `backend/tests/` | Idle |

---

## 🔄 Workflow Nhanh

```
Architect → Tạo Task → Backend → Code API → UI → Code Screen → Testing → Tests → ✅
```

---

## 📝 Task Status

- **PENDING**: Chưa bắt đầu, đợi dependency
- **IN_PROGRESS**: Đang làm, Agent khác không được can thiệp
- **COMPLETED**: Đã xong, có thể hand-off
- **BLOCKED**: Bị chặn bởi dependency

---

## 🔧 MCP Tools

1. **MCP Filesystem**: Đọc/ghi files
2. **MCP Terminal**: Chạy commands (test, build, lint)
3. **MCP Git**: Tự động commit (nếu có)

---

## ⚠️ Quy Tắc Quan Trọng

1. ✅ **LUÔN** đọc `shared_state.json` trước
2. ✅ **LUÔN** cập nhật khi hoàn thành
3. ❌ **KHÔNG** can thiệp task IN_PROGRESS của Agent khác
4. ✅ **GHI** vào `shared_memory.active_constants` khi tạo component/function mới

---

## 📚 Tài Liệu Chi Tiết

- **Vai trò đầy đủ**: `.mcp/AGENT_ROLES.md`
- **Hướng dẫn MCP**: `.mcp/MCP_USAGE_GUIDE.md`
- **Workflow demo**: `docs/WORKFLOW_DEMO.md`

---

**Last Updated:** 2025-12-17

