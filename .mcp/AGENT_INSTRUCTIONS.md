# Hướng Dẫn Cho Các Agent - Đọc Prompt Từ Dashboard

## 🎯 Cách Hoạt Động

1. **User gửi message từ Dashboard** → Tạo file `.mcp/pending_prompts/{Agent}.md`
2. **Agent đọc file** và thực hiện yêu cầu
3. **Agent cập nhật** `shared_state.json` khi hoàn thành

## 📋 Prompt Để Copy Vào Mỗi Chat Agent

### Architect Chat
```
Bạn là Agent Architect. Khi tôi gõ "sync" hoặc "đọc prompt", hãy:
1. Đọc file .mcp/pending_prompts/Architect.md
2. Thực hiện yêu cầu trong file đó
3. Cập nhật .mcp/shared_state.json nếu cần
```

### Backend_AI_Dev Chat
```
Bạn là Agent Backend_AI_Dev. Khi tôi gõ "sync" hoặc "đọc prompt", hãy:
1. Đọc file .mcp/pending_prompts/Backend_AI_Dev.md
2. Thực hiện yêu cầu trong file đó
3. Cập nhật .mcp/shared_state.json nếu cần
```

### UI_UX_Dev Chat
```
Bạn là Agent UI_UX_Dev. Khi tôi gõ "sync" hoặc "đọc prompt", hãy:
1. Đọc file .mcp/pending_prompts/UI_UX_Dev.md
2. Thực hiện yêu cầu trong file đó
3. Cập nhật .mcp/shared_state.json nếu cần
```

### Testing_QA Chat
```
Bạn là Agent Testing_QA. Khi tôi gõ "sync" hoặc "đọc prompt", hãy:
1. Đọc file .mcp/pending_prompts/Testing_QA.md
2. Thực hiện yêu cầu trong file đó
3. Cập nhật .mcp/shared_state.json nếu cần
```

### Supervisor Chat
```
Bạn là Agent Supervisor. Khi tôi gõ "sync" hoặc "đọc prompt", hãy:
1. Đọc file .mcp/pending_prompts/Supervisor.md
2. Thực hiện yêu cầu trong file đó
3. Cập nhật .mcp/shared_state.json nếu cần
```

## 🔄 Workflow

1. **Mở Dashboard**: `http://localhost:8000/.mcp/dashboard_enhanced.html`
2. **Gửi message**: Tab "Trigger Agent" → Chọn Agent → Nhập message → Send
3. **Trong chat của Agent đó**: Gõ `sync` hoặc `đọc prompt`
4. Agent sẽ đọc prompt file và thực hiện

## 📁 Cấu Trúc File

```
.mcp/
├── pending_prompts/
│   ├── Architect.md          ← Prompt cho Architect
│   ├── Backend_AI_Dev.md     ← Prompt cho Backend_AI_Dev
│   ├── UI_UX_Dev.md          ← Prompt cho UI_UX_Dev
│   ├── Testing_QA.md         ← Prompt cho Testing_QA
│   └── Supervisor.md         ← Prompt cho Supervisor
├── shared_state.json         ← State chung
└── trigger_queue.json        ← Queue các triggers
```

## ✨ Tips

- Mỗi lần gửi message mới từ Dashboard, prompt file sẽ được **ghi đè**
- Agent nên đọc prompt file **ngay sau khi nhận notification** từ Dashboard
- Sau khi xử lý xong, agent nên **cập nhật shared_state.json** để các agent khác biết






