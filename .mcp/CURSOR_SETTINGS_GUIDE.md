# Hướng Dẫn Cấu Hình Cursor Settings Cho 4 Agent

## 🎯 Auto-Approved Mode Transitions

Tính năng này cho phép tự động approve các chuyển đổi giữa các Agent mà không cần prompt thủ công, giúp workflow mượt mà và nhanh hơn.

---

## ✅ Các Transitions Nên Auto-Approve

Dựa trên workflow của 4 Agent, bạn nên cấu hình các transitions sau trong Cursor Settings:

### 1. **Architect → Backend_AI_Dev**
```
architect->backend
architect->backend_ai_dev
```
**Lý do:** Khi Architect tạo task và hand-off cho Backend Agent, transition này nên tự động để Backend có thể bắt đầu ngay.

### 2. **Backend_AI_Dev → UI_UX_Dev**
```
backend->ui
backend_ai_dev->ui_ux_dev
backend->frontend
```
**Lý do:** Sau khi Backend hoàn thành API, UI Agent cần bắt đầu implement ngay, không cần chờ approve.

### 3. **UI_UX_Dev → Testing_QA**
```
ui->testing
ui_ux_dev->testing_qa
frontend->testing
```
**Lý do:** Sau khi UI hoàn thành, Testing Agent cần test ngay để đảm bảo quality.

### 4. **Testing_QA → Architect** (nếu cần fix)
```
testing->architect
testing_qa->architect
testing->plan
```
**Lý do:** Nếu có bug cần fix, Testing có thể báo lại Architect để tạo task mới.

### 5. **Backend_AI_Dev → Testing_QA** (direct)
```
backend->testing
backend_ai_dev->testing_qa
```
**Lý do:** Backend có thể hand-off trực tiếp cho Testing để test API.

---

## 📋 Cấu Hình Trong Cursor Settings

### Cách 1: Nhập Từng Dòng (Khuyến Nghị)
Trong field "Auto-Approved Mode Transitions", nhập từng dòng:

```
architect->backend
architect->backend_ai_dev
backend->ui
backend_ai_dev->ui_ux_dev
backend->frontend
ui->testing
ui_ux_dev->testing_qa
frontend->testing
testing->architect
testing_qa->architect
testing->plan
backend->testing
backend_ai_dev->testing_qa
```

### Cách 2: Pattern Matching (Nếu Hỗ Trợ)
Nếu Cursor hỗ trợ pattern, có thể dùng:
```
*->backend
*->ui
*->testing
backend->*
ui->*
testing->architect
```

---

## 🔄 Workflow Với Auto-Approve

### Scenario: Xây dựng tính năng Search

1. **Architect** tạo task → Auto-approve → **Backend_AI_Dev** nhận task
2. **Backend_AI_Dev** code API → Auto-approve → **UI_UX_Dev** implement UI
3. **UI_UX_Dev** code screen → Auto-approve → **Testing_QA** test
4. **Testing_QA** hoàn thành → Auto-approve → **Architect** review (nếu cần)

**Kết quả:** Toàn bộ workflow chạy tự động, không cần approve thủ công ở mỗi bước!

---

## ⚠️ Lưu Ý

### Nên Auto-Approve:
- ✅ Hand-off giữa các Agent theo workflow chuẩn
- ✅ Transitions đã được định nghĩa trong `AGENT_ROLES.md`
- ✅ Các task có dependencies rõ ràng

### KHÔNG Nên Auto-Approve:
- ❌ Architect → Testing (bỏ qua Backend/UI)
- ❌ Testing → Backend (bỏ qua Architect)
- ❌ Các transitions không theo workflow

---

## 🎯 Best Practices

1. **Bắt đầu với ít transitions:** Chỉ auto-approve các transitions chắc chắn
2. **Monitor workflow:** Xem các transitions nào thường xuyên xảy ra
3. **Điều chỉnh dần:** Thêm/bớt transitions dựa trên thực tế sử dụng
4. **Document:** Ghi lại các transitions đã cấu hình trong file này

---

## 📝 Template Cấu Hình

Copy và paste vào Cursor Settings:

```
# Auto-Approved Mode Transitions for 4-Agent System
# Format: from_agent->to_agent

# Architect hand-offs
architect->backend
architect->backend_ai_dev
architect->plan

# Backend hand-offs
backend->ui
backend_ai_dev->ui_ux_dev
backend->frontend
backend->testing
backend_ai_dev->testing_qa

# UI hand-offs
ui->testing
ui_ux_dev->testing_qa
frontend->testing

# Testing hand-offs (nếu cần fix)
testing->architect
testing_qa->architect
testing->plan
```

---

## 🔍 Kiểm Tra Cấu Hình

Sau khi cấu hình, test bằng cách:

1. **Architect** tạo task và hand-off cho **Backend**
2. Kiểm tra xem có prompt approve không
3. Nếu không có prompt → ✅ Đã cấu hình đúng
4. Nếu vẫn có prompt → Kiểm tra lại format trong settings

---

## 💡 Tips

- **Sử dụng alias:** Nếu Cursor hỗ trợ, có thể dùng alias ngắn gọn hơn
- **Wildcard:** Nếu có, dùng `*` để match nhiều patterns
- **Case sensitive:** Kiểm tra xem Cursor có phân biệt hoa thường không

---

**Last Updated:** 2025-12-17  
**Maintained by:** Agent Architect

