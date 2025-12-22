# Cách Bật Auto-Accept Edits Trong Cursor

## 🎯 Vấn Đề

Bạn phải bấm "Accept" mỗi lần AI suggest code edit → Mất thời gian, gián đoạn workflow.

## ✅ Giải Pháp: Bật Auto-Accept

### Cách 1: Settings UI (Khuyến Nghị)

1. **Mở Cursor Settings:**
   - macOS: `Cmd + ,`
   - Windows/Linux: `Ctrl + ,`

2. **Tìm "Auto-apply":**
   - Search box: gõ `auto-apply` hoặc `auto accept`
   - Hoặc vào: **Features** → **Composer** → **Auto-apply**

3. **Bật các options:**
   - ✅ **Auto-apply edits**: Tự động accept edits
   - ✅ **Auto-apply for single edits**: Accept ngay khi chỉ có 1 edit
   - ⚠️ **Auto-apply for multiple edits**: Cẩn thận với nhiều edits cùng lúc

### Cách 2: Settings JSON

1. **Mở Settings JSON:**
   - `Cmd/Ctrl + Shift + P` → Gõ "Preferences: Open User Settings (JSON)"

2. **Thêm config:**
```json
{
  "cursor.cpp.autoApply": true,
  "cursor.composer.autoApply": true,
  "cursor.chat.autoApply": true,
  "cursor.chat.autoApplySingleEdit": true,
  "cursor.chat.autoApplyMultipleEdits": false
}
```

### Cách 3: Per-File Type Auto-Accept

Nếu chỉ muốn auto-accept cho một số file types:

```json
{
  "[dart]": {
    "cursor.chat.autoApply": true
  },
  "[python]": {
    "cursor.chat.autoApply": true
  },
  "[typescript]": {
    "cursor.chat.autoApply": true
  }
}
```

---

## ⚙️ Các Options Chi Tiết

### 1. **Auto-apply Single Edit** (Khuyến Nghị)
- ✅ Tự động accept khi chỉ có 1 edit
- ✅ An toàn, ít risk
- ✅ Phù hợp cho workflow nhanh

### 2. **Auto-apply Multiple Edits**
- ⚠️ Tự động accept nhiều edits cùng lúc
- ⚠️ Có thể có risk nếu edits phức tạp
- 💡 Chỉ bật nếu bạn tin tưởng AI 100%

### 3. **Auto-apply with Delay**
- ⏱️ Delay vài giây trước khi auto-apply
- ✅ Cho bạn thời gian review
- ✅ Vẫn tự động nhưng an toàn hơn

---

## 🎯 Best Practice

### Cho Multi-Agent Workflow:

**Khuyến Nghị:**
```json
{
  "cursor.chat.autoApplySingleEdit": true,
  "cursor.chat.autoApplyMultipleEdits": false,
  "cursor.chat.autoApplyDelay": 2000  // 2 giây delay
}
```

**Lý do:**
- ✅ Single edit auto-accept → Nhanh cho small changes
- ❌ Multiple edits manual → Review kỹ trước khi accept
- ⏱️ Delay 2s → Có thời gian cancel nếu cần

---

## 🔧 Advanced: Conditional Auto-Accept

Nếu muốn auto-accept chỉ cho một số trường hợp:

### Option 1: By File Pattern
```json
{
  "cursor.chat.autoApply": {
    "enabled": true,
    "patterns": [
      "**/*.dart",
      "**/backend/**/*.py"
    ],
    "exclude": [
      "**/test/**",
      "**/*_test.dart"
    ]
  }
}
```

### Option 2: By Agent Role
Có thể config trong MCP settings để auto-accept cho:
- Backend_AI_Dev → Auto-accept Python files
- UI_UX_Dev → Auto-accept Dart files
- Testing_QA → Manual review (không auto-accept)

---

## ⚠️ Lưu Ý

### Khi Nào KHÔNG Nên Auto-Accept:

1. **Critical Files:**
   - `shared_state.json` → Nên review manual
   - `main.dart`, `main.py` → Entry points quan trọng
   - Database migrations → Cần review kỹ

2. **Large Refactors:**
   - Nhiều files cùng lúc
   - Thay đổi architecture
   - Breaking changes

3. **Testing Phase:**
   - Khi đang test code
   - Khi có nhiều conflicts

---

## 🚀 Quick Setup

### Copy & Paste Vào Settings JSON:

```json
{
  // Auto-accept settings
  "cursor.chat.autoApplySingleEdit": true,
  "cursor.chat.autoApplyMultipleEdits": false,
  "cursor.chat.autoApplyDelay": 1000,
  
  // Per-file type
  "[dart]": {
    "cursor.chat.autoApply": true
  },
  "[python]": {
    "cursor.chat.autoApply": true
  }
}
```

---

## 📋 Checklist

- [ ] Mở Cursor Settings
- [ ] Tìm "Auto-apply" hoặc "Auto-accept"
- [ ] Bật "Auto-apply single edit"
- [ ] Test với một edit nhỏ
- [ ] Điều chỉnh delay nếu cần
- [ ] Exclude critical files nếu cần

---

## 💡 Tips

1. **Bắt đầu với single edit auto-accept:**
   - An toàn hơn
   - Vẫn tiết kiệm thời gian

2. **Review sau mỗi session:**
   - Check git diff
   - Revert nếu có vấn đề

3. **Sử dụng Git:**
   - Commit thường xuyên
   - Dễ revert nếu auto-accept sai

---

**Last Updated:** 2025-12-17  
**Maintained by:** Agent Architect

