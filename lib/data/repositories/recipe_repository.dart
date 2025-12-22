import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/recipe_model.dart';
import '../services/firestore_service.dart';
import '../../core/constants/app_constants.dart';

/// Recipe Repository - Data Layer
/// Handles all recipe-related database operations
class RecipeRepository {
  final FirestoreService _firestoreService;

  RecipeRepository({FirestoreService? firestoreService})
      : _firestoreService = firestoreService ?? FirestoreService();

  /// Get all recipes
  Future<List<RecipeModel>> getAllRecipes() async {
    try {
      final snapshot = await _firestoreService.recipesCollection.get();
      return snapshot.docs
          .map((doc) => RecipeModel.fromFirestore(doc.data(), doc.id))
          .toList();
    } catch (e) {
      throw Exception('Failed to get all recipes: $e');
    }
  }

  /// Get recipe by ID
  Future<RecipeModel?> getRecipeById(String id) async {
    try {
      final doc = await _firestoreService.recipesCollection.doc(id).get();
      if (!doc.exists) return null;
      return RecipeModel.fromFirestore(doc.data()!, doc.id);
    } catch (e) {
      throw Exception('Failed to get recipe by ID: $e');
    }
  }

  /// Search recipes by calories range
  /// This is the function referenced in task T003
  Future<List<RecipeModel>> searchByCalories(int minCal, int maxCal) async {
    try {
      final snapshot = await _firestoreService.recipesCollection
          .where('calories', isGreaterThanOrEqualTo: minCal)
          .where('calories', isLessThanOrEqualTo: maxCal)
          .get();
      
      return snapshot.docs
          .map((doc) => RecipeModel.fromFirestore(doc.data(), doc.id))
          .toList();
    } catch (e) {
      throw Exception('Failed to search recipes by calories: $e');
    }
  }

  /// Search recipes by ingredients
  Future<List<RecipeModel>> searchByIngredients(List<String> ingredients) async {
    try {
      // Firestore doesn't support array-contains-all directly, so we'll filter client-side
      final snapshot = await _firestoreService.recipesCollection.get();
      final allRecipes = snapshot.docs
          .map((doc) => RecipeModel.fromFirestore(doc.data(), doc.id))
          .toList();

      // Filter recipes that contain at least one of the search ingredients
      return allRecipes.where((recipe) {
        return ingredients.any((ingredient) =>
            recipe.ingredients.any((rIngredient) =>
                rIngredient.toLowerCase().contains(ingredient.toLowerCase())));
      }).toList();
    } catch (e) {
      throw Exception('Failed to search recipes by ingredients: $e');
    }
  }

  /// Search recipes by difficulty
  Future<List<RecipeModel>> searchByDifficulty(String difficulty) async {
    try {
      final snapshot = await _firestoreService.recipesCollection
          .where('difficulty', isEqualTo: difficulty)
          .get();
      
      return snapshot.docs
          .map((doc) => RecipeModel.fromFirestore(doc.data(), doc.id))
          .toList();
    } catch (e) {
      throw Exception('Failed to search recipes by difficulty: $e');
    }
  }

  /// Search recipes by cooking time (max time in minutes)
  Future<List<RecipeModel>> searchByCookingTime(int maxTime) async {
    try {
      final snapshot = await _firestoreService.recipesCollection
          .where('cooking_time', isLessThanOrEqualTo: maxTime)
          .get();
      
      return snapshot.docs
          .map((doc) => RecipeModel.fromFirestore(doc.data(), doc.id))
          .toList();
    } catch (e) {
      throw Exception('Failed to search recipes by cooking time: $e');
    }
  }

  /// Create a new recipe
  Future<String> createRecipe(RecipeModel recipe) async {
    try {
      final docRef = await _firestoreService.recipesCollection
          .add(recipe.toFirestore());
      return docRef.id;
    } catch (e) {
      throw Exception('Failed to create recipe: $e');
    }
  }

  /// Update an existing recipe
  Future<void> updateRecipe(RecipeModel recipe) async {
    try {
      await _firestoreService.recipesCollection
          .doc(recipe.id)
          .update(recipe.toFirestore());
    } catch (e) {
      throw Exception('Failed to update recipe: $e');
    }
  }

  /// Delete a recipe
  Future<void> deleteRecipe(String id) async {
    try {
      await _firestoreService.recipesCollection.doc(id).delete();
    } catch (e) {
      throw Exception('Failed to delete recipe: $e');
    }
  }

  /// Stream all recipes (real-time updates)
  Stream<List<RecipeModel>> streamAllRecipes() {
    return _firestoreService.recipesCollection
        .snapshots()
        .map((snapshot) => snapshot.docs
            .map((doc) => RecipeModel.fromFirestore(doc.data(), doc.id))
            .toList());
  }

  /// Stream recipe by ID (real-time updates)
  Stream<RecipeModel?> streamRecipeById(String id) {
    return _firestoreService.recipesCollection
        .doc(id)
        .snapshots()
        .map((doc) => doc.exists
            ? RecipeModel.fromFirestore(doc.data()!, doc.id)
            : null);
  }
}

