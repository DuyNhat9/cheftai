import 'package:cloud_firestore_mocks/cloud_firestore_mocks.dart';
import 'package:cheftai/core/constants/app_constants.dart';

/// Helper class for creating mock Firestore data in tests
class MockFirestoreHelper {
  final MockFirestoreInstance mockFirestore;

  MockFirestoreHelper(this.mockFirestore);

  /// Add a test recipe to mock Firestore
  Future<String> addTestRecipe({
    required String name,
    required int calories,
    required List<String> ingredients,
    required int cookingTime,
    required String difficulty,
  }) async {
    final docRef = await mockFirestore
        .collection(AppConstants.recipesCollection)
        .add({
      'name': name,
      'calories': calories,
      'ingredients': ingredients,
      'cooking_time': cookingTime,
      'difficulty': difficulty,
    });
    return docRef.id;
  }

  /// Add multiple test recipes
  Future<List<String>> addTestRecipes(List<Map<String, dynamic>> recipes) async {
    final ids = <String>[];
    for (var recipe in recipes) {
      final docRef = await mockFirestore
          .collection(AppConstants.recipesCollection)
          .add(recipe);
      ids.add(docRef.id);
    }
    return ids;
  }

  /// Clear all recipes from mock Firestore
  Future<void> clearRecipes() async {
    final snapshot = await mockFirestore
        .collection(AppConstants.recipesCollection)
        .get();
    for (var doc in snapshot.docs) {
      await doc.reference.delete();
    }
  }
}


