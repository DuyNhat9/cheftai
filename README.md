# 🍳 CheftAi Android

> AI-Powered Recipe App cho Android - Tìm công thức nấu ăn thông minh với AI

## 📱 Giới thiệu

CheftAi là ứng dụng Android giúp người dùng tìm kiếm công thức nấu ăn dựa trên nguyên liệu có sẵn, sử dụng AI (Google Gemini) để gợi ý món ăn phù hợp nhất.

## 🏗️ Tech Stack

- **Frontend:** Flutter (Dart) + Material Design 3
- **Backend:** FastAPI (Python) + Google Gemini API
- **Database:** Firestore (Firebase)
- **Architecture:** Clean Architecture / MVVM

## 🚀 Tính năng

- 🔍 Tìm kiếm công thức theo nguyên liệu
- 📸 Scan nguyên liệu bằng Camera (AI Vision)
- 🎯 Gợi ý món ăn cá nhân hóa theo sở thích
- 📊 Theo dõi calo và dinh dưỡng
- 💾 Lưu công thức yêu thích offline

## 🤖 Multi-Agent Development

Dự án này sử dụng mô hình **Multi-Agent Collaboration** với MCP (Model Context Protocol) để phối hợp **4 Agent**:

- **Agent Architect:** Thiết kế cấu trúc hệ thống, quản lý task board
- **Agent UI/UX Dev:** Phát triển giao diện Flutter với Material Design 3
- **Agent Backend & AI Dev:** Xử lý logic, tích hợp Google Gemini API
- **Agent Testing & QA:** Viết tests, kiểm tra code quality

Xem chi tiết tại:
- [`.mcp/AGENT_ROLES.md`](.mcp/AGENT_ROLES.md) - Vai trò và quy tắc của từng Agent
- [`.mcp/MCP_USAGE_GUIDE.md`](.mcp/MCP_USAGE_GUIDE.md) - Hướng dẫn sử dụng MCP
- [`docs/WORKFLOW_DEMO.md`](docs/WORKFLOW_DEMO.md) - Demo workflow Multi-Agent

## 📂 Cấu trúc dự án

```
cheftAi/
├── .mcp/                          # Multi-Agent Collaboration Protocol
│   ├── shared_state.json          # Trạng thái chung cho 4 Agent
│   ├── AGENT_ROLES.md             # Vai trò và quy tắc của 4 Agent
│   └── MCP_USAGE_GUIDE.md         # Hướng dẫn sử dụng MCP
├── docs/                          # Tài liệu dự án
│   ├── WORKFLOW_DEMO.md           # Demo workflow Multi-Agent
│   ├── MCP_GIT_DEMO.md            # Demo MCP Git Automation
│   ├── PROJECT_STRUCTURE.md       # Cấu trúc thư mục
│   └── schema.md                  # Schema database
├── scripts/                       # Utility scripts
└── [Flutter project structure - coming soon]
```

## 🛠️ Setup

### Yêu cầu
- Flutter SDK 3.0+
- Python 3.10+
- Google Gemini API Key

### Cài đặt
```bash
# Clone repository
git clone https://github.com/DuyNhat9/cheftai.git
cd cheftai

# Setup Flutter (coming soon)
# flutter pub get

# Setup Backend (coming soon)
# cd backend && pip install -r requirements.txt
```

## 📝 License

MIT License

## 👥 Contributors

- [DuyNhat9](https://github.com/DuyNhat9)

---

**Status:** 🚧 Đang phát triển - Multi-Agent Infrastructure đã sẵn sàng!

