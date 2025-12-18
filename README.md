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

Dự án này sử dụng mô hình **Multi-Agent Collaboration** với MCP (Model Context Protocol) để phối hợp 3 Agent:

- **Agent Architect:** Thiết kế cấu trúc hệ thống
- **Agent UI/UX Dev:** Phát triển giao diện Flutter
- **Agent Backend & AI Dev:** Xử lý logic và tích hợp AI

Xem chi tiết tại [AGENT_ROLES.md](./AGENT_ROLES.md) và [WORKFLOW_DEMO.md](./WORKFLOW_DEMO.md)

## 📂 Cấu trúc dự án

```
cheftAi/
├── shared_state.json      # Trạng thái chung cho Multi-Agent
├── AGENT_ROLES.md         # Quy tắc phối hợp Agent
├── WORKFLOW_DEMO.md       # Demo workflow Multi-Agent
├── schema.md              # Schema database
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

