# Tests cho CheftAi Backend

## Tổng quan

Test suite cho FastAPI backend của CheftAi Android app, sử dụng pytest framework.

## Cấu trúc

```
backend/tests/
├── __init__.py
├── conftest.py              # Pytest configuration và shared fixtures
├── test_api_recipes_generate.py  # Tests cho /api/recipes/generate endpoint
├── requirements.txt         # Test dependencies
└── README.md               # Tài liệu này
```

## Cài đặt

```bash
cd backend/tests
pip install -r requirements.txt
```

## Chạy Tests

### Chạy tất cả tests
```bash
pytest
```

### Chạy với verbose output
```bash
pytest -v
```

### Chạy một file test cụ thể
```bash
pytest test_api_recipes_generate.py
```

### Chạy với coverage report
```bash
pytest --cov=backend --cov-report=html
```

### Chạy tests theo marker
```bash
# Chỉ chạy integration tests
pytest -m integration

# Chỉ chạy performance tests
pytest -m performance
```

## Test Coverage cho T008

### Success Cases (5 tests)
- ✅ Basic recipe generation với valid ingredients
- ✅ Recipe generation với dietary preferences (vegan, vegetarian)
- ✅ Recipe generation với minimal ingredients
- ✅ Recipe generation với custom servings
- ✅ Recipe generation với nhiều ingredients

### Error Cases (8 tests)
- ✅ Missing ingredients
- ✅ Empty ingredients list
- ✅ Invalid ingredients type
- ✅ Invalid servings (negative/zero)
- ✅ Gemini API failure
- ✅ Gemini API timeout
- ✅ Invalid JSON request
- ✅ Missing required fields
- ✅ Invalid dietary preferences
- ✅ Invalid Gemini response format

### Edge Cases (2 tests)
- ✅ Many ingredients (10+)
- ✅ Special characters in ingredient names

### Integration Tests (2 tests)
- ⏳ Full flow integration (requires actual backend)
- ⏳ Database save integration (requires Firestore)

### Performance Tests (1 test)
- ✅ Response time < 5 seconds

## Lưu ý

1. **Mocking**: Tests sử dụng `unittest.mock` để mock Google Gemini API calls
2. **Fixtures**: Shared fixtures được định nghĩa trong `conftest.py`
3. **Integration Tests**: Một số integration tests yêu cầu backend thực tế đang chạy
4. **Environment**: Tests cần được chạy trong môi trường test riêng biệt

## Task T008 Status

- **Status**: ✅ COMPLETED
- **Owner**: Testing_QA
- **Test File**: `test_api_recipes_generate.py`
- **Total Tests**: 18 test cases

## Next Steps

Khi backend code được implement, cần:
1. Update import paths trong test files
2. Chạy tests để verify implementation
3. Fix any failing tests
4. Đạt coverage target 80%

