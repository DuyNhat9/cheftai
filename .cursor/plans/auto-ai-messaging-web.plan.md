---
name: auto-ai-messaging-web
overview: Lên kế hoạch cho project web cho phép Architect (Sonnet 4.5) tự hiểu codebase CheftAi, phân tích yêu cầu và chia task tự động cho các Agent còn lại (Backend_AI_Dev, UI_UX_Dev, Testing_QA) thông qua MCP + dashboard.
todos:
  - id: planner-setup-architect
    agent: Architect
    content: Thiết kế kiến trúc tổng thể cho web app gửi tin nhắn tự động cho các Agent AI, đọc docs/HOW_MULTI_AGENT_WORKS.md và .mcp/shared_state.json hiện tại, sau đó mô tả high-level flow (kiểu sequence diagram) cho việc Architect nhận yêu cầu, tạo tasks và trigger các agent khác qua dashboard.
    status: pending

  - id: planner-define-agent-contracts
    agent: Architect
    content: Định nghĩa rõ vai trò và contract cho 4 agent trong bối cảnh project web mới (Architect planner, Backend_AI_Dev cho API + MCP integration, UI_UX_Dev cho web UI React/Vite, Testing_QA cho tests); cập nhật hoặc bổ sung vào docs/AGENT_MONITORING.md và .mcp/AGENT_ROLES.md nếu cần.
    status: pending
    dependencies:
      - planner-setup-architect

  - id: backend-design-web-api
    agent: Backend_AI_Dev
    content: Thiết kế và (ở mức skeleton) implement các endpoint backend phục vụ web app gửi tin nhắn cho agents, ví dụ /api/agents, /api/messages, /api/triggers; mô tả cách kết nối với hệ MCP hiện tại (shared_state.json, trigger_queue.json, pending_prompts/*).
    status: pending
    dependencies:
      - planner-define-agent-contracts

  - id: uiux-design-web-dashboard
    agent: UI_UX_Dev
    content: Thiết kế và phác thảo UI cho web dashboard mới (React/Vite) cho phép chọn Agent (Architect, Backend_AI_Dev, UI_UX_Dev, Testing_QA), nhập message, xem lịch sử hội thoại, và nút auto-trigger tasks; tham khảo .mcp/dashboard_enhanced.html hiện tại.
    status: pending
    dependencies:
      - planner-define-agent-contracts

  - id: testing-plan-web-flow
    agent: Testing_QA
    content: Lên test plan cho flow web → MCP → Agents, bao gồm tests cho API (FastAPI/pytest), sanity check cho UI (playwright/cypress hoặc test thủ công được mô tả rõ ràng), và checklist để verify rằng tasks mới luôn cập nhật chính xác trong .mcp/shared_state.json.
    status: pending
    dependencies:
      - backend-design-web-api
      - uiux-design-web-dashboard
---

## Kế hoạch Project Web: Gửi tin nhắn tự động cho các Agent AI

### Mục tiêu

- **Mục tiêu chính**: Có một web app (dashboard mới hoặc mở rộng dashboard hiện tại) cho phép:
  - Người dùng nhập yêu cầu một lần cho **Architect (Sonnet 4.5)**.
  - Architect đọc context project, lên kế hoạch và chia nhỏ công việc cho các Agent còn lại.
  - Người dùng có thể trigger từng task/agent ngay trong web.
- **Tận dụng MCP sẵn có**: Sử dụng `.mcp/shared_state.json`, `trigger_queue.json`, `pending_prompts/*` và `dashboard_enhanced.html` thay vì viết lại từ đầu.

### Phân rã công việc theo Agent

- **Architect**:
  - Chuẩn hoá flow planner → tasks → trigger agents.
  - Cập nhật docs và shared_state để các agent khác dễ follow.

- **Backend_AI_Dev**:
  - Cung cấp API layer để web app có thể:
    - Lấy danh sách agents & tasks (task_board).
    - Gửi message/yêu cầu cho Architect.
    - Trigger tác vụ cho agent khác thông qua MCP/dashboards.

- **UI_UX_Dev**:
  - Thiết kế và build web UI trực quan, ưu tiên:
    - Dễ nhìn trạng thái từng Agent.
    - Dễ nhập prompt cho Architect & các Agent.
    - Hiển thị log/hoạt động gần đây.

- **Testing_QA**:
  - Đảm bảo các luồng quan trọng (gửi yêu cầu, Architect chia task, trigger agent, cập nhật shared_state) hoạt động ổn định.
  - Thiết kế test plan có thể chạy lại nhanh khi refactor.


