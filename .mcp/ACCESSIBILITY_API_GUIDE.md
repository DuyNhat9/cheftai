# Accessibility API Guide - Tìm Chat Input trong Cursor

## Tổng quan

Không có extension cụ thể cho Cursor để xác định vị trí chat input. Thay vào đó, chúng ta sử dụng **macOS Accessibility API** thông qua AppleScript để tìm và tương tác với UI elements.

## Cách hoạt động

### 1. Accessibility API trong AppleScript

AppleScript có thể truy cập UI elements thông qua `System Events`:

```applescript
tell application "System Events"
    tell process "Cursor"
        -- Tìm text fields
        set textFields to (text fields of window 1)
        
        -- Tìm text areas
        set textAreas to (text areas of window 1)
        
        -- Click vào element
        perform action "AXPress" of textFields[1]
    end tell
end tell
```

### 2. Logic hiện tại trong `auto_submit_service.py`

Code đã được cập nhật để:

1. **Đóng tất cả file editor** (Cmd+W nhiều lần)
2. **Mở chat panel** (Cmd+L)
3. **Sử dụng Accessibility API** để tìm text field/area trong chat panel
4. **Click vào chat input** để focus
5. **Fallback về keyboard shortcut** nếu Accessibility API fail

### 3. Test Accessibility API

Chạy script test để xem các UI elements có sẵn:

```bash
python3 .mcp/test_accessibility_chat_input.py
```

Script này sẽ:
- Mở chat panel (Cmd+L)
- Liệt kê tất cả text fields, text areas, scroll areas, groups
- Log thông tin về role và name của mỗi element

## Các phương pháp khác

### Phương pháp 1: Keyboard Shortcuts (Hiện tại)

**Ưu điểm:**
- Đơn giản, không phụ thuộc vào UI structure
- Hoạt động với mọi version của Cursor

**Nhược điểm:**
- Không chắc chắn 100% focus vào đúng element
- Có thể paste vào editor nếu timing không đúng

### Phương pháp 2: Accessibility API (Đã thêm)

**Ưu điểm:**
- Tìm element chính xác
- Click trực tiếp vào chat input

**Nhược điểm:**
- Phụ thuộc vào UI structure của Cursor
- Có thể thay đổi khi Cursor update
- Cần permission "Accessibility" trong System Preferences

### Phương pháp 3: Image Detection (Đã thử, không hiệu quả)

**Nhược điểm:**
- Phức tạp, cần dependencies (pyautogui, opencv)
- Không reliable với different screen sizes/resolutions
- Chậm

## Cấu hình Accessibility Permission

Để sử dụng Accessibility API, cần:

1. Mở **System Preferences** → **Security & Privacy** → **Privacy** → **Accessibility**
2. Thêm Terminal hoặc Python vào danh sách allowed apps
3. Hoặc chạy script và macOS sẽ tự động prompt

## Debugging

Nếu Accessibility API không hoạt động:

1. Kiểm tra permission:
   ```bash
   python3 .mcp/test_accessibility_chat_input.py
   ```

2. Xem debug logs trong `auto_submit_service.py`:
   - `DEBUG_CHAT_INPUT_FOUND_VIA_ACCESSIBILITY` - Tìm thấy bằng Accessibility API
   - `DEBUG_CHAT_INPUT_FALLBACK_TO_KEYBOARD` - Fallback về keyboard shortcut

3. Kiểm tra UI structure:
   - Mở Cursor
   - Mở chat panel (Cmd+L)
   - Chạy test script để xem các elements có sẵn

## Kết luận

Hiện tại, **không có extension** nào cho Cursor để xác định vị trí chat input. Giải pháp tốt nhất là:

1. **Kết hợp Accessibility API + Keyboard Shortcuts** (đã implement)
2. **Đóng tất cả file editor** trước khi paste
3. **Tăng delay** để đảm bảo UI đã load
4. **Fallback** về keyboard shortcut nếu Accessibility API fail

