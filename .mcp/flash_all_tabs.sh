#!/bin/bash
# Flash/highlight tất cả agent tabs đang mở

echo "✨ Flashing all agent tabs..."
echo "============================================================"

# Option 1: Dùng API endpoint
if curl -s http://localhost:8001/api/flash-tabs > /dev/null 2>&1; then
    response=$(curl -s http://localhost:8001/api/flash-tabs)
    success=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)
    
    if [ "$success" = "True" ]; then
        echo "✅ Successfully flashed all tabs via API"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    else
        echo "⚠️  API call failed, trying direct method..."
        python3 .mcp/test_flash_tabs.py
    fi
else
    echo "⚠️  API server not running, using direct method..."
    python3 .mcp/test_flash_tabs.py
fi

echo ""
echo "💡 Tất cả các tabs đã được focus lần lượt để làm nháy"

