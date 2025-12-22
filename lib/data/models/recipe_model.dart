import 'package:equatable/equatable.dart';

/// Recipe Model - Data Layer
/// Maps to Firestore 'recipes' collection
class RecipeModel extends Equatable {
  final String id;
  final String name;
  final int calories;
  final List<String> ingredients;
  final int cookingTime; // in minutes
  final String difficulty; // Easy/Medium/Hard

  const RecipeModel({
    required this.id,
    required this.name,
    required this.calories,
    required this.ingredients,
    required this.cookingTime,
    required this.difficulty,
  });

  /// Create RecipeModel from Firestore document
  factory RecipeModel.fromFirestore(Map<String, dynamic> doc, String id) {
    return RecipeModel(
      id: id,
      name: doc['name'] ?? '',
      calories: doc['calories'] ?? 0,
      ingredients: List<String>.from(doc['ingredients'] ?? []),
      cookingTime: doc['cooking_time'] ?? 0,
      difficulty: doc['difficulty'] ?? 'Easy',
    );
  }

  /// Convert RecipeModel to Firestore document
  Map<String, dynamic> toFirestore() {
    return {
      'name': name,
      'calories': calories,
      'ingredients': ingredients,
      'cooking_time': cookingTime,
      'difficulty': difficulty,
    };
  }

  /// Create a copy with updated fields
  RecipeModel copyWith({
    String? id,
    String? name,
    int? calories,
    List<String>? ingredients,
    int? cookingTime,
    String? difficulty,
  }) {
    return RecipeModel(
      id: id ?? this.id,
      name: name ?? this.name,
      calories: calories ?? this.calories,
      ingredients: ingredients ?? this.ingredients,
      cookingTime: cookingTime ?? this.cookingTime,
      difficulty: difficulty ?? this.difficulty,
    );
  }

  @override
  List<Object?> get props => [id, name, calories, ingredients, cookingTime, difficulty];

  @override
  String toString() {
    return 'RecipeModel(id: $id, name: $name, calories: $calories, cookingTime: $cookingTime, difficulty: $difficulty)';
  }
}

