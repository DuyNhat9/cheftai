# Cấu trúc thư mục CheftAi

## 📁 Tổng quan

Dự án được tổ chức theo chuẩn chuyên nghiệp, phân loại rõ ràng các file theo mục đích sử dụng.

## 🗂️ Cấu trúc chi tiết

```
cheftAi/
├── 📄 README.md                    # Tài liệu chính của dự án
├── 📄 .gitignore                   # Git ignore rules
│
├── 🤖 .mcp/                        # Multi-Agent Collaboration Protocol
│   ├── shared_state.json           # Trạng thái chung cho 4 Agent
│   ├── AGENT_ROLES.md              # Vai trò và quy tắc của 4 Agent
│   └── MCP_USAGE_GUIDE.md          # Hướng dẫn sử dụng MCP cho các Agent
│
├── 📚 docs/                        # Tài liệu dự án
│   ├── WORKFLOW_DEMO.md            # Demo workflow Multi-Agent
│   ├── MCP_GIT_DEMO.md             # Demo MCP Git Automation
│   ├── schema.md                   # Database schema
│   └── research/                   # Nghiên cứu và tài liệu tham khảo
│       └── Grok-Websites for App Keyword Research.md
│
├── 🔧 scripts/                     # Utility scripts
│   └── demo_mcp_git.sh             # Demo script cho MCP Git
│
└── 📱 [Flutter project - coming soon]
    ├── lib/                        # Flutter source code
    ├── android/                    # Android native code
    ├── ios/                        # iOS native code (nếu cần)
    └── test/                       # Unit tests
```

## 📖 Giải thích từng thư mục

### 🤖 `.mcp/` - Multi-Agent Collaboration
**Mục đích:** Chứa các file liên quan đến hệ thống Multi-Agent Collaboration

**Files:**
- `shared_state.json`: File trạng thái chung, 4 Agent đọc/ghi để đồng bộ công việc. Chứa:
  - `project_info`: Thông tin dự án
  - `shared_memory`: Constants, tech stack, project structure
  - `agents`: Trạng thái của 4 Agent (Architect, UI_UX_Dev, Backend_AI_Dev, Testing_QA)
  - `task_board`: Danh sách tasks và dependencies
- `AGENT_ROLES.md`: Định nghĩa vai trò, nhiệm vụ và quy tắc của 4 Agent
- `MCP_USAGE_GUIDE.md`: Hướng dẫn chi tiết cách sử dụng MCP tools, workflow, và best practices

**Lưu ý:** 
- **TẤT CẢ 4 Agent PHẢI đọc `shared_state.json` TRƯỚC khi bắt đầu làm việc**
- Tuân thủ giao thức MCP: READ BEFORE ACT, UPDATE ON SUCCESS, LOCKING

---

### 📚 `docs/` - Tài liệu
**Mục đích:** Lưu trữ tất cả tài liệu liên quan đến dự án

**Files:**
- `WORKFLOW_DEMO.md`: Hướng dẫn chi tiết workflow Multi-Agent
- `MCP_GIT_DEMO.md`: Demo cách MCP tự động hóa Git workflow
- `schema.md`: Cấu trúc database (tables, relationships)

**Subdirectory:**
- `research/`: Tài liệu nghiên cứu, keyword research, market analysis

---

### 🔧 `scripts/` - Utility Scripts
**Mục đích:** Các script hỗ trợ phát triển và automation

**Files:**
- `demo_mcp_git.sh`: Demo script cho MCP Git Automation

**Lưu ý:** Tất cả scripts phải có quyền execute (`chmod +x`).

---

### 📄 Root Level
**Files quan trọng:**
- `README.md`: Tài liệu chính, giới thiệu dự án
- `.gitignore`: Git ignore rules cho Flutter/Android/Python

---

## 🎯 Quy tắc sử dụng

1. **MCP Files:** Chỉ Agent mới được sửa file trong `.mcp/`
2. **Documentation:** Tất cả tài liệu mới phải đặt trong `docs/`
3. **Scripts:** Scripts mới phải đặt trong `scripts/` và có quyền execute
4. **Research:** Tài liệu nghiên cứu đặt trong `docs/research/`

---

## 🚀 Cấu trúc sắp tới (Flutter Project)

Khi khởi tạo Flutter project, cấu trúc sẽ như sau:

```
lib/
├── core/              # Core utilities, constants
├── data/              # Data layer (repositories, models)
├── domain/             # Business logic (use cases, entities)
├── presentation/       # UI layer (screens, widgets, viewmodels)
└── main.dart          # Entry point

android/               # Android native code
ios/                   # iOS native code (nếu cần)
test/                  # Unit tests
```

---

**Last Updated:** 2025-12-17
**Maintained by:** Agent Architect











