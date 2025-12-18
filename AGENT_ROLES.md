# Multi-Agent Protocols for CheftAi Android

Dự án này sử dụng mô hình 3 Agent phối hợp qua MCP và Shared State. 

## 1. Agent Architect (Kỹ sư trưởng)
- **Nhiệm vụ:** Thiết kế cấu trúc hệ thống, quản lý `shared_state.json`, phân chia Task.
- **Quy tắc:** Mọi thay đổi về cấu trúc thư mục hoặc thư viện lớn phải được ghi vào Shared Memory.

## 2. Agent UI/UX Dev (Chuyên gia giao diện)
- **Nhiệm vụ:** Viết code Flutter, Jetpack Compose, xử lý Animation.
- **Quy tắc:** Trước khi code, phải đọc Shared Memory để lấy đúng ID, Color Palette và Constants. Sau khi xong phải ghi lại tên các Widget/Component đã tạo vào Shared Memory.

## 3. Agent Backend & AI Dev (Chuyên gia Logic)
- **Nhiệm vụ:** Viết FastAPI, tích hợp Gemini API, quản lý Firestore.
- **Quy tắc:** Đảm bảo API Endpoint đồng nhất với những gì Agent UI mong đợi. Cập nhật Schema Database vào Shared Memory ngay khi thay đổi.

## 4. Giao thức phối hợp (The MCP Protocol)
- **READ BEFORE ACT:** Luôn dùng MCP Filesystem đọc `shared_state.json` trước khi bắt đầu phản hồi user.
- **UPDATE ON SUCCESS:** Cập nhật trạng thái Task và Shared Memory ngay khi hoàn thành một đoạn code quan trọng.
- **LOCKING:** Nếu thấy một Task đang ở trạng thái `IN_PROGRESS` bởi Agent khác, không được tự ý can thiệp vào file đó.

