---
name: phase3-ui-ux-polish
overview: Lên kế hoạch cho Phase tiếp theo tập trung polish UI/UX của CheftAi với phạm vi nhỏ (1–2 tuần), ưu tiên trải nghiệm thực tế trên app Flutter hiện tại, tận dụng multi-agent MCP.
todos:
  - id: define-ui-ux-guidelines
    content: Architect rà soát flow hiện tại và tạo UI_UX_GUIDE.md với user flow + guideline ngắn cho 3 màn chính
    status: pending
  - id: implement-flutter-polish
    content: UI_UX_Dev polish 3 màn Flutter chính (onboarding, ingredient input, recipe result) + tách shared widgets
    status: pending
    dependencies:
      - define-ui-ux-guidelines
  - id: prepare-backend-support
    content: Backend_AI_Dev đảm bảo API/mock data ổn định cho demo UI và cập nhật backend/README.md
    status: pending
    dependencies:
      - define-ui-ux-guidelines
  - id: create-ux-testing-checklist
    content: Testing_QA tạo TESTING_UX_CHECKLIST.md và UX_ISSUES_BACKLOG.md, chạy qua app sau khi UI polish
    status: pending
    dependencies:
      - implement-flutter-polish
      - prepare-backend-support
  - id: update-shared-state-phase3
    content: Cập nhật .mcp/shared_state.json với task_board Phase 3 và trạng thái project_info.status mới
    status: pending
    dependencies:
      - define-ui-ux-guidelines
---

## Kế hoạch Phase tiếp theo: UI/UX Polish ( phạm vi nhỏ 1–2 tuần )

### 1. Mục tiêu tổng quan

- **Hoàn thiện trải nghiệm UI/UX lõi** cho CheftAi trên Flutter: onboarding, nhập nguyên liệu, xem kết quả gợi ý.
- **Giữ nguyên backend hiện tại**, chỉ tinh chỉnh UI, navigation và feedback cho người dùng.
- **Tối ưu cho multi-agent**: chia việc rõ ràng cho 4 agent qua `shared_state.json` và dashboard.

### 2. Phân rã Phase thành 4 track theo agent

#### 2.1 Architect – Thiết kế UX flow & guideline

- **Nhiệm vụ chính**:
- Rà soát lại flow hiện tại trong các màn:
    - `lib/presentation/screens/onboarding_screen.dart`
    - `lib/presentation/screens/ingredient_input_screen.dart`
    - `lib/presentation/screens/recipe_result_screen.dart`
- Vẽ **user flow đơn giản** cho 3 bước chính: Onboarding → Nhập nguyên liệu → Xem kết quả.
- Định nghĩa **UI guideline ngắn** (Design Tokens + Components):
    - Cách dùng `app_theme.dart` (color, typography, elevation).
    - Chuẩn hoá spacing, corner radius, icon style.
    - Quy ước đặt tên widgets/shared components.
- Cập nhật tài liệu trong:
    - [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md) (phần Flutter UI structure).
    - Tạo file mới [`docs/UI_UX_GUIDE.md`](docs/UI_UX_GUIDE.md) mô tả flow & guideline.
- **Deliverables**:
- `UI_UX_GUIDE.md` rõ ràng, ngắn gọn.
- Cập nhật `shared_state.json` với các task mới cho UI/UX.

#### 2.2 UI_UX_Dev – Polish giao diện Flutter

- **Nhiệm vụ chính** (theo guideline Architect):
- **Onboarding** (`onboarding_screen.dart`):
    - Chuẩn hoá typography, spacing, button style theo `app_theme.dart`.
    - Thêm **page indicator + nhẹ animation** (fade/slide) khi chuyển step.
- **Ingredient Input** (`ingredient_input_screen.dart`):
    - Cải thiện form input (chips, tags, validation message rõ ràng).
    - Thêm trạng thái loading / empty / error.
    - Chuẩn hoá layout cho mobile nhỏ.
- **Recipe Result** (`recipe_result_screen.dart`, `recipe_card.dart`):
    - Thêm **hero / implicit animations** khi mở chi tiết món (nếu đã có layout phù hợp).
    - Cải thiện card layout (ảnh, rating, calo, tags).
    - Thêm pull-to-refresh hoặc nút reload rõ ràng.
- Tách ra một số **reusable widgets** (nếu cần) trong `lib/presentation/widgets/`:
    - `primary_button.dart`, `section_title.dart`, `loading_overlay.dart`, v.v.
- **Deliverables**:
- PR chỉnh sửa file Flutter UI chính: onboarding, input, result, widgets.
- Screenshot trước/sau (ghi vào [`docs/UI_UX_GUIDE.md`](docs/UI_UX_GUIDE.md) hoặc `docs/WORKFLOW_STATUS.md`).

#### 2.3 Backend_AI_Dev – Hỗ trợ UI & mock data

- **Nhiệm vụ chính** (nhẹ, hỗ trợ cho UI phase):
- Cập nhật FastAPI để có **endpoint mock data ổn định** phục vụ demo UI:
    - Kiểm tra lại [`backend/app/routes/recipes.py`](backend/app/routes/recipes.py) & services.
    - Đảm bảo có 1–2 request mẫu trả về kết quả nhanh, ổn định.
- Nếu cần, tạo **mock layer** hoặc sample JSON để UI team dùng offline:
    - Ví dụ: [`backend/tests/data/sample_recipes.json`](backend/tests/data/sample_recipes.json) (nếu chưa có, sẽ bổ sung trong phase code).
- Viết mô tả ngắn trong [`backend/README.md`](backend/README.md) cách gọi API cho Flutter.
- **Deliverables**:
- Backend sẵn sàng để UI test nhanh.
- Tài liệu API ngắn, đủ để UI_UX_Dev sử dụng.

#### 2.4 Testing_QA – Kiểm tra UX & Regression đơn giản

- **Nhiệm vụ chính**:
- Viết **checklist UX** đơn giản trong [`docs/TESTING_UX_CHECKLIST.md`](docs/TESTING_UX_CHECKLIST.md):
    - Flow 3 màn chính không bị kẹt / dead end.
    - Text không tràn, UI không vỡ ở một vài kích thước màn hình.
    - Loading/error state hiển thị đúng.
- Thêm **1–2 UI tests đơn giản** (nếu setup phù hợp) hoặc hướng dẫn test tay rõ ràng.
- Ghi nhận bug/issue vào `docs/WORKFLOW_STATUS.md` hoặc file mới `docs/UX_ISSUES_BACKLOG.md`.
- **Deliverables**:
- Checklist UX + danh sách issue.
- Gợi ý ưu tiên cho phase kế tiếp (nếu còn nhiều bug/ý tưởng).

### 3. Cập nhật MCP & shared_state cho phase mới

- Thêm các task Phase UI Polish vào `task_board` trong [`.mcp/shared_state.json`](.mcp/shared_state.json), gán rõ `owner` cho 4 agent.
- Đặt trạng thái ban đầu cho tất cả task mới là `PENDING`, và cập nhật `project_info.status` thành kiểu: `"Phase 3 – UI Polish (In Progress)"`.
- Đảm bảo dashboard mới `.mcp/dashboard_modern.html` đọc được các task này và hiển thị đúng.

### 4. Cách sử dụng dashboard & auto-trigger trong Phase này

- Dùng tab Agents trên `dashboard_modern.html` để:
- Trigger từng agent khi ready với task tương ứng (theo `owner`).
- Xem trạng thái `Idle` / `Working` và task hiện tại.
- Khi agent hoàn thành, yêu cầu agent **update `shared_state.json`** (status task + agent) để dashboard sync.
- Nếu cần, bổ sung mô tả ngắn vào [`.mcp/AGENT_AUTO_TRIGGER.md`](.mcp/AGENT_AUTO_TRIGGER.md) về cách sử dụng cho Phase 3.

### 5. Ưu tiên thực thi (theo thời gian)

1. **Architect**: cập nhật flow + `UI_UX_GUIDE.md` (nền tảng cho phần còn lại).
2. **UI_UX_Dev**: implement polish trên 3 màn chính + widgets tái sử dụng.
3. **Backend_AI_Dev**: tinh chỉnh mock data/API để hỗ trợ UI test.
4. **Testing_QA**: tạo checklist UX + ghi nhận issues sau khi UI update xong.

Khi bạn đồng ý plan này, bước tiếp theo sẽ là:

- Tạo/cập nhật các file docs (`UI_UX_GUIDE.md`, checklist, backlog).