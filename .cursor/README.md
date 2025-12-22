# Cursor Settings Configuration

## 🚀 Quick Setup

### Cách 1: Copy từ File (Nhanh nhất)

1. Mở file: `.cursor/cursor_settings_transitions.txt`
2. Copy tất cả nội dung (Cmd/Ctrl + A, Cmd/Ctrl + C)
3. Mở Cursor Settings:
   - macOS: `Cmd + ,`
   - Windows/Linux: `Ctrl + ,`
4. Tìm "Auto-Approved Mode Transitions" trong search box
5. Paste vào field đó
6. Save

### Cách 2: Dùng Script (macOS)

```bash
cd /Users/davidtran/Documents/cheftAi
./scripts/setup_cursor_settings.sh
```

Script sẽ hiển thị hướng dẫn và nội dung cần copy.

### Cách 3: Copy trực tiếp

Copy các dòng sau vào Cursor Settings:

```
architect->backend
architect->backend_ai_dev
architect->plan
backend->ui
backend_ai_dev->ui_ux_dev
backend->frontend
backend->testing
backend_ai_dev->testing_qa
ui->testing
ui_ux_dev->testing_qa
frontend->testing
testing->architect
testing_qa->architect
testing->plan
```

---

## ✅ Kiểm Tra

Sau khi cấu hình:
1. Architect tạo task và hand-off cho Backend
2. Nếu không có prompt approve → ✅ Thành công!
3. Nếu vẫn có prompt → Kiểm tra lại format

---

## 📚 Tài Liệu Chi Tiết

Xem `.mcp/CURSOR_SETTINGS_GUIDE.md` để biết thêm chi tiết.

