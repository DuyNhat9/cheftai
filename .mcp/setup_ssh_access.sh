#!/bin/bash
# Script để setup SSH access cho Cursor workspace
# Cho phép truy cập từ xa thông qua SSH

echo "🔧 Setting up SSH access for Cursor workspace..."

# Kiểm tra SSH server
if ! system_profiler SPApplicationsDataType 2>/dev/null | grep -q "Remote Login"; then
    echo "⚠️  SSH server chưa được enable"
    echo "   Mở System Settings > General > Sharing > Remote Login"
    echo "   Hoặc chạy: sudo systemsetup -setremotelogin on"
    read -p "Bạn có muốn enable SSH server bây giờ? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo systemsetup -setremotelogin on
        echo "✅ SSH server đã được enable"
    fi
fi

# Lấy IP address
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "localhost")
echo ""
echo "📡 SSH Access Information:"
echo "   IP Address: $IP"
echo "   Username: $(whoami)"
echo "   Port: 22"
echo ""
echo "🔗 Connect từ máy khác:"
echo "   ssh $(whoami)@$IP"
echo ""
echo "📦 Port Forwarding (để truy cập API servers từ xa):"
echo "   ssh -L 8000:localhost:8000 -L 8001:localhost:8001 $(whoami)@$IP"
echo ""
echo "🌐 Sau khi forward ports, truy cập:"
echo "   Dashboard: http://localhost:8000/.mcp/dashboard_enhanced.html"
echo "   API: http://localhost:8001/api/state"
echo ""

