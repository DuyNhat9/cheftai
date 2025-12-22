# 🎯 Prompt Template cho Architect (Agent Chính)

Khi bạn muốn Architect lên plan và tự động trigger các worker agents, dùng prompt này:

## 📋 Prompt Mẫu:

```
Lên plan cho task: [MÔ TẢ TASK]

Yêu cầu:
1. Đọc .mcp/shared_state.json để hiểu context hiện tại
2. Phân tích task và chia thành các subtasks cho các worker agents:
   - Backend_AI_Dev: [Các task backend/API]
   - UI_UX_Dev: [Các task UI/UX]
   - Testing_QA: [Các task testing/QA]
   - Supervisor: [Các task giám sát nếu cần]
3. Cập nhật shared_state.json:
   - Thêm tasks vào task_board với status "PENDING"
   - Mỗi task có: id, title, owner, status, description
4. Sau khi update xong, gọi API: POST http://localhost:8001/api/notify-change (optional, monitor sẽ tự detect)

Ví dụ format task:
{
  "id": "B201",
  "title": "Backend: Implement API endpoint X",
  "owner": "Backend_AI_Dev",
  "status": "PENDING",
  "description": "Chi tiết task..."
}
```

## 🔄 Flow Tự Động:

1. **Architect nhận prompt** → Lên plan
2. **Architect update shared_state.json** → Thêm tasks với status "PENDING"
3. **Monitor service tự động detect** → Trigger worker agents
4. **Workers nhận prompt** → Làm việc và update status

## 💡 Tips:

- Architect chỉ cần update shared_state.json, không cần trigger thủ công
- Monitor service sẽ tự động phát hiện và trigger
- Mỗi task PENDING sẽ được trigger một lần (tránh duplicate)
- Task status sẽ tự động update: PENDING → IN_PROGRESS → COMPLETED

## 📝 Ví dụ Thực Tế:

```
Lên plan cho task: Thêm tính năng favorite recipes vào CheftAi app

Yêu cầu:
1. Đọc .mcp/shared_state.json
2. Chia task thành:
   - Backend: API endpoint GET/POST /api/favorites
   - UI: Screen hiển thị favorite recipes với icon heart
   - Testing: Test cases cho favorite flow
3. Update shared_state.json với các tasks PENDING
4. Monitor service sẽ tự động trigger workers
```

