# Setup Instructions - CheftAi Android

## Task T009: Firestore Connection & Recipe Repository - COMPLETED ✅

### What was implemented:

1. **Firestore Service** (`lib/data/services/firestore_service.dart`)
   - Singleton pattern for Firestore connection
   - Offline persistence enabled
   - Collection references for recipes and user_favorites

2. **Recipe Model** (`lib/data/models/recipe_model.dart`)
   - Maps to Firestore schema from `docs/schema.md`
   - fromFirestore/toFirestore conversion methods
   - Equatable for value comparison

3. **Recipe Repository** (`lib/data/repositories/recipe_repository.dart`)
   - CRUD operations (Create, Read, Update, Delete)
   - `searchByCalories()` - Ready for task T003
   - `searchByIngredients()` - For ingredient-based search
   - `searchByDifficulty()` - Filter by difficulty level
   - `searchByCookingTime()` - Filter by max cooking time
   - Real-time streams for reactive updates

4. **Project Structure** (Clean Architecture)
   ```
   lib/
   ├── core/
   │   └── constants/
   │       └── app_constants.dart
   ├── data/
   │   ├── models/
   │   │   └── recipe_model.dart
   │   ├── repositories/
   │   │   └── recipe_repository.dart
   │   └── services/
   │       └── firestore_service.dart
   └── main.dart
   ```

### Next Steps:

1. **Setup Firebase Project:**
   - Create Firebase project at https://console.firebase.google.com
   - Add Android app to Firebase project
   - Download `google-services.json` and place in `android/app/`
   - Update `android/build.gradle` and `android/app/build.gradle`

2. **Install Dependencies:**
   ```bash
   flutter pub get
   ```

3. **Test Firestore Connection:**
   - Run app: `flutter run`
   - Check Firebase console for connection

4. **Add Sample Data:**
   - Use Firebase Console to add test recipes
   - Or create a data seeding script

### Dependencies Added:
- `firebase_core: ^2.24.2`
- `cloud_firestore: ^4.13.6`
- `flutter_bloc: ^8.1.3` (for future state management)
- `equatable: ^2.0.5` (for model comparison)

