# Multi-Agent Dashboard - Hướng Dẫn Sử Dụng

## 🎯 Mục Đích

Dashboard trực quan để monitor 4 Agents đang làm việc, không cần phải:
- ❌ Xem từng chat window
- ❌ Check file shared_state.json thủ công
- ❌ Đoán Agent nào đang làm gì

## 🚀 Cách Mở Dashboard

### Cách 1: Dùng Script (Nhanh nhất)
```bash
cd /Users/davidtran/Documents/cheftAi
./scripts/open_dashboard.sh
```

### Cách 2: Mở Trực Tiếp
1. Mở file: `.mcp/dashboard.html`
2. Kéo thả vào browser
3. Hoặc right-click → "Open with" → Browser

### Cách 3: Từ Terminal
```bash
# macOS
open .mcp/dashboard.html

# Linux
xdg-open .mcp/dashboard.html

# Windows
start .mcp/dashboard.html
```

---

## 📊 Tính Năng Dashboard

### 1. **Agent Status Cards**
- Hiển thị 4 Agents với status (Working/Idle)
- Current task của mỗi Agent
- Visual indicators (màu sắc, badges)

### 2. **Task Board**
- Danh sách tất cả tasks
- Filter theo status (All/Completed/In Progress/Pending)
- Progress bar tổng thể
- Task details (owner, dependencies, files created)

### 3. **Statistics**
- Total tasks
- Completed tasks
- In Progress tasks
- Pending tasks

### 4. **Auto-Refresh**
- Tự động refresh mỗi 5 giây
- Manual refresh button
- Countdown timer

---

## 🎨 Giao Diện

### Color Coding:
- 🟢 **Green**: Working/Completed
- 🟣 **Purple**: In Progress
- 🟡 **Yellow**: Pending
- ⚪ **Gray**: Idle

### Visual Indicators:
- **Working Agent**: Card có border màu xanh, glow effect
- **Completed Task**: Border màu xanh lá
- **In Progress Task**: Border màu tím
- **Pending Task**: Border màu vàng

---

## 🔧 Cách Hoạt Động

1. **Dashboard đọc file:** `.mcp/shared_state.json`
2. **Parse JSON:** Lấy thông tin agents và tasks
3. **Render UI:** Hiển thị trực quan
4. **Auto-refresh:** Tự động reload mỗi 5 giây

---

## ⚠️ Lưu Ý

### CORS Issue (Nếu có):
Nếu browser block việc đọc file local, có thể:
1. **Dùng local server:**
```bash
# Python
cd /Users/davidtran/Documents/cheftAi
python3 -m http.server 8000
# Mở: http://localhost:8000/.mcp/dashboard.html
```

2. **Hoặc dùng VS Code Live Server extension**

### File Path:
Dashboard cần file `.mcp/shared_state.json` ở cùng level hoặc relative path đúng.

---

## 💡 Tips

1. **Pin Dashboard:**
   - Mở dashboard trong browser tab riêng
   - Pin tab để luôn thấy

2. **Multiple Monitors:**
   - Mở dashboard trên màn hình thứ 2
   - Theo dõi real-time trong khi code

3. **Bookmark:**
   - Bookmark dashboard URL
   - Mở nhanh khi cần

---

## 🐛 Troubleshooting

### Dashboard không load data:
- ✅ Check file `.mcp/shared_state.json` tồn tại
- ✅ Check browser console (F12) xem có lỗi không
- ✅ Thử dùng local server thay vì file://

### Auto-refresh không hoạt động:
- ✅ Check JavaScript console
- ✅ Reload page (F5)
- ✅ Check browser không block auto-refresh

---

**Last Updated:** 2025-12-17  
**Maintained by:** Agent Architect

