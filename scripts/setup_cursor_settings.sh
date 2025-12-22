#!/bin/bash
# Script hướng dẫn cập nhật Cursor Settings cho 4-Agent System

echo "🚀 Setup Cursor Settings cho 4-Agent System"
echo "=============================================="
echo ""

# Đường dẫn file transitions
TRANSITIONS_FILE=".cursor/cursor_settings_transitions.txt"

if [ ! -f "$TRANSITIONS_FILE" ]; then
    echo "❌ Không tìm thấy file: $TRANSITIONS_FILE"
    exit 1
fi

echo "📋 Các Auto-Approved Mode Transitions:"
echo "--------------------------------------"
cat "$TRANSITIONS_FILE"
echo ""
echo ""

echo "📝 Hướng dẫn cập nhật:"
echo "--------------------------------------"
echo "1. Mở Cursor Settings:"
echo "   - macOS: Cmd + ,"
echo "   - Windows/Linux: Ctrl + ,"
echo ""
echo "2. Tìm 'Auto-Approved Mode Transitions' trong search box"
echo ""
echo "3. Copy tất cả các dòng từ file: $TRANSITIONS_FILE"
echo ""
echo "4. Paste vào field 'Auto-Approved Mode Transitions'"
echo ""
echo "5. Save settings"
echo ""
echo "✅ Hoàn thành!"
echo ""
echo "💡 Tips:"
echo "   - Bạn có thể mở file .cursor/cursor_settings_transitions.txt để copy"
echo "   - Hoặc dùng lệnh: cat $TRANSITIONS_FILE | pbcopy (macOS)"
echo ""

