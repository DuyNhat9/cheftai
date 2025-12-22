# Test Suite for CheftAi

## Unit Tests for searchByCalories

### Test File
- `test/data/repositories/recipe_repository_test.dart`

### Test Coverage

The unit tests for `searchByCalories()` cover:

1. **Method Signature Verification**
   - Verifies method exists and has correct signature
   - Tests parameter acceptance

2. **Boundary Cases**
   - Equal min and max calories
   - Zero calories
   - Large calorie ranges
   - Reverse range (min > max)

3. **Return Type Verification**
   - Ensures method returns `Future<List<RecipeModel>>`

4. **Integration Test Placeholders**
   - Documents expected behavior for integration tests
   - Requires Firebase emulator or test project

### Running Tests

#### Unit Tests (Current)
```bash
flutter test test/data/repositories/recipe_repository_test.dart
```

#### Integration Tests (Requires Setup)
1. Start Firebase Emulator:
   ```bash
   firebase emulators:start --only firestore
   ```

2. Configure app to use emulator (in test setup)

3. Run integration tests:
   ```bash
   flutter test test/data/repositories/recipe_repository_test.dart
   ```

### Dependencies

Tests use:
- `flutter_test` (built-in)
- `mockito` (for mocking - if needed)
- `cloud_firestore_mocks` (for Firestore mocking - if needed)

### Future Improvements

1. **Make FirestoreService Injectable**
   - Refactor `FirestoreService` to accept `FirebaseFirestore` instance
   - Allows easier mocking in tests

2. **Add Mock Tests**
   - Use `cloud_firestore_mocks` for comprehensive mocking
   - Test actual Firestore queries without real database

3. **Add Integration Tests**
   - Set up Firebase emulator
   - Test with real Firestore queries
   - Verify data persistence

4. **Add Widget Tests**
   - Test UI components that use `searchByCalories`
   - Verify UI updates correctly with results

### Test Structure

```
test/
├── data/
│   └── repositories/
│       └── recipe_repository_test.dart
├── helpers/
│   └── mock_firestore_helper.dart
└── README.md
```


