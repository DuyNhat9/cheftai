# 🌐 Remote Access Guide - Cursor Workspace via SSH

Hướng dẫn truy cập Cursor workspace từ xa thông qua SSH.

## 📋 Prerequisites

1. **Enable SSH trên máy Mac:**
   ```bash
   sudo systemsetup -setremotelogin on
   ```
   Hoặc: System Settings > General > Sharing > Remote Login

2. **Lấy IP address:**
   ```bash
   ipconfig getifaddr en0
   # hoặc
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

## 🔧 Setup

### 1. Chạy setup script:
```bash
chmod +x .mcp/setup_ssh_access.sh
./mcp/setup_ssh_access.sh
```

### 2. Start servers:
```bash
chmod +x .mcp/start_remote_servers.sh
./mcp/start_remote_servers.sh
```

## 🔗 Connect từ máy khác

### Option 1: SSH với Port Forwarding (Khuyến nghị)

Từ máy client, chạy:
```bash
ssh -L 8000:localhost:8000 -L 8001:localhost:8001 username@server_ip
```

Sau đó mở browser trên máy client:
- Dashboard: http://localhost:8000/.mcp/dashboard_enhanced.html
- API: http://localhost:8001/api/state

### Option 2: VS Code Remote SSH

1. Install extension: **Remote - SSH**
2. Cmd+Shift+P > "Remote-SSH: Connect to Host"
3. Nhập: `username@server_ip`
4. Chọn workspace folder
5. Mở terminal và chạy servers

### Option 3: Cursor Remote SSH (nếu hỗ trợ)

Tương tự VS Code Remote SSH.

## 📡 Ports

- **8000**: Dashboard server
- **8001**: API server
- **22**: SSH (default)

## 🛠️ Useful Commands

### Start servers:
```bash
./mcp/start_remote_servers.sh
```

### Stop servers:
```bash
pkill -f api_server.py
pkill -f dashboard_server.py
```

### Check server status:
```bash
ps aux | grep -E "(api_server|dashboard_server)" | grep -v grep
```

### View logs:
```bash
tail -f /tmp/api_server.log
tail -f /tmp/dashboard_server.log
```

### Send message từ remote terminal:
```bash
python3 .mcp/send_message.py Architect "Hello from remote"
```

## 🔒 Security Tips

1. **Use SSH keys instead of password:**
   ```bash
   ssh-copy-id username@server_ip
   ```

2. **Change SSH port (optional):**
   - Edit `/etc/ssh/sshd_config`
   - Change `Port 22` to another port
   - Restart: `sudo launchctl unload /System/Library/LaunchDaemons/ssh.plist && sudo launchctl load /System/Library/LaunchDaemons/ssh.plist`

3. **Firewall:**
   - Chỉ mở ports cần thiết
   - Sử dụng VPN nếu có thể

## 🐛 Troubleshooting

### SSH không connect được:
- Kiểm tra SSH server: `sudo systemsetup -getremotelogin`
- Kiểm tra firewall
- Kiểm tra IP address

### Port forwarding không hoạt động:
- Kiểm tra servers đang chạy: `ps aux | grep api_server`
- Kiểm tra ports không bị block: `lsof -i :8000 -i :8001`

### Servers không start:
- Kiểm tra logs: `tail /tmp/api_server.log`
- Kiểm tra Python version: `python3 --version`
- Kiểm tra ports đã được dùng: `lsof -i :8000 -i :8001`

