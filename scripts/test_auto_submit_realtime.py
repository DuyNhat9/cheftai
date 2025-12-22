#!/usr/bin/env python3
"""
Test script để debug auto_submit_service realtime
"""
import subprocess
import sys
from pathlib import Path

# Test với một message đơn giản
agent = "Architect"
message = "TEST REALTIME DEBUG - Nếu bạn thấy message này trong Cursor chat thì auto-submit đang hoạt động"
worktree_id = "hng"
model = "Sonnet 4.5"

# Tạo prompt file
prompt_file = Path(".mcp/pending_prompts/test_realtime.md")
prompt_file.parent.mkdir(exist_ok=True)
prompt_file.write_text(f"# Test Message\n\n{message}\n", encoding='utf-8')

print(f"📝 Created prompt file: {prompt_file}")
print(f"📄 Content preview: {message[:50]}...")
print()

# Gọi auto_submit_service
cmd = [
    'python3',
    '.mcp/auto_submit_service.py',
    agent,
    str(prompt_file.resolve()),
    worktree_id,
    model
]

print(f"🔧 Running command:")
print(f"   {' '.join(cmd)}")
print()

result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    timeout=20
)

print("=" * 60)
print("STDOUT:")
print("=" * 60)
print(result.stdout)
print()

if result.stderr:
    print("=" * 60)
    print("STDERR:")
    print("=" * 60)
    print(result.stderr)
    print()

print("=" * 60)
print(f"Return Code: {result.returncode}")
print("=" * 60)

# Phân tích kết quả
if "sent_to_cursor_ok" in result.stdout:
    print("\n✅ Status: sent_to_cursor_ok")
    print("⚠️  QUAN TRỌNG: Kiểm tra xem Cursor có thực sự nhận được message không!")
    print("   - Mở Cursor chat của Architect")
    print("   - Xem có message 'TEST REALTIME DEBUG' không")
elif "app_not_running" in result.stdout:
    print("\n❌ Cursor không chạy")
elif "no_windows" in result.stdout:
    print("\n❌ Không tìm thấy Cursor window")
elif "window_not_found" in result.stdout:
    print("\n❌ Không tìm thấy window phù hợp")
elif "osascript_failed" in result.stdout:
    print("\n❌ AppleScript failed - có lỗi trong quá trình gửi")
else:
    print("\n⚠️  Status không rõ ràng")
    print("   Cần kiểm tra logs chi tiết hơn")

