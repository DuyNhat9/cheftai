# Multi-Agent Workflow Demo: Search Feature

## Scenario: Xây dựng tính năng "Search Món Ăn theo Calo"

### Bước 1: Agent Architect (Planner)
**Prompt cho Agent Architect:**
```
> Làm Planner Agent: Phân tích tính năng search món ăn theo calo. 
Chia task cho Backend (logic query), UI (Compose screen), Testing (unit tests).
Đọc shared_state.json để xem task hiện tại.
```

**Agent Architect sẽ:**
1. Đọc `shared_state.json` → Thấy Task T003, T004, T005 đang PENDING
2. Phân tích: T003 phải làm trước (Backend), T004 phụ thuộc T003 (UI), T005 test T003
3. Cập nhật `shared_state.json`: Đánh dấu T003 là `IN_PROGRESS`, owner = "Backend_AI_Dev"

---

### Bước 2: Agent Backend (Hand-off từ Architect)
**Prompt cho Agent Backend:**
```
> Backend Agent: Viết hàm searchByCalories trong RecipeRepository.kt, 
dùng MCP đọc schema.md để lấy table name. 
Hand-off: Changes: Added function. Next: UI Agent.
```

**Agent Backend sẽ:**
1. Đọc `shared_state.json` → Thấy T003 đang `IN_PROGRESS`, owner là mình
2. Dùng MCP Filesystem đọc `schema.md` → Biết table `recipes` có field `calories: Int`
3. Viết code:
   ```kotlin
   fun searchByCalories(minCal: Int, maxCal: Int): List<Recipe> {
       return db.recipeDao().searchByCalories(minCal, maxCal)
   }
   ```
4. Cập nhật `shared_state.json`:
   - T003 status → `COMPLETED`
   - Ghi vào `shared_memory.active_constants`: `{"search_function": "searchByCalories"}`
   - T004 status → `IN_PROGRESS`, owner = "UI_UX_Dev"

---

### Bước 3: Agent UI (Hand-off từ Backend)
**Prompt cho Agent UI:**
```
> UI Agent: Build SearchScreen.kt với Jetpack Compose, 
kết nối hàm từ Backend. 
Hand-off: Changes: Added screen. Next: Testing.
```

**Agent UI sẽ:**
1. Đọc `shared_state.json` → Thấy T004 đang `IN_PROGRESS`, owner là mình
2. Đọc `shared_memory.active_constants` → Biết tên hàm là `searchByCalories`
3. Dùng MCP Filesystem đọc file Backend vừa tạo → Biết interface chính xác
4. Viết code:
   ```kotlin
   @Composable
   fun SearchScreen(viewModel: RecipeViewModel) {
       val results = viewModel.searchByCalories(100, 500)
       // ... UI code
   }
   ```
5. Cập nhật `shared_state.json`:
   - T004 status → `COMPLETED`
   - Ghi vào `shared_memory`: `{"ui_component": "SearchScreen.kt"}`

---

### Bước 4: Agent Testing (Hand-off từ UI)
**Prompt cho Agent Testing:**
```
> Testing Agent: Viết unit tests cho searchByCalories, 
dùng MCP run build.gradle để check compile.
```

**Agent Testing sẽ:**
1. Đọc `shared_state.json` → Thấy T005 đang PENDING, dependency T003 đã COMPLETED
2. Dùng MCP Terminal chạy: `./gradlew test` để verify
3. Viết test:
   ```kotlin
   @Test
   fun testSearchByCalories() {
       val results = repo.searchByCalories(100, 500)
       assertEquals(3, results.size)
   }
   ```
4. Cập nhật `shared_state.json`: T005 status → `COMPLETED`

---

## Kết quả:
- ✅ Toàn bộ tính năng hoàn thành trong 20-30 phút
- ✅ Code đồng bộ, không crash
- ✅ Mỗi Agent biết chính xác việc của mình
- ✅ Không có xung đột file hay duplicate code

## Pro Tips:
1. **Commit sau mỗi hand-off** để track changes
2. **Dùng MCP Filesystem** để đọc file thay vì đoán
3. **Luôn cập nhật shared_state.json** trước khi chuyển task

