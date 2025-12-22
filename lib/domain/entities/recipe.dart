/// Recipe Entity - Domain Model
class Recipe {
  final String id;
  final String name;
  final int calories;
  final List<String> ingredients;
  final int cookingTime; // minutes
  final String difficulty; // Easy, Medium, Hard
  final String? imageUrl;
  final String? description;
  final double? rating;
  final int? servings;
  final List<String>? tags; // e.g., ["Vegan", "Italian", "Quick & Easy"]

  Recipe({
    required this.id,
    required this.name,
    required this.calories,
    required this.ingredients,
    required this.cookingTime,
    required this.difficulty,
    this.imageUrl,
    this.description,
    this.rating,
    this.servings,
    this.tags,
  });

  /// Factory constructor từ JSON (cho API response)
  factory Recipe.fromJson(Map<String, dynamic> json) {
    return Recipe(
      id: json['id'] as String,
      name: json['name'] as String,
      calories: json['calories'] as int,
      ingredients: List<String>.from(json['ingredients'] as List),
      cookingTime: json['cooking_time'] as int,
      difficulty: json['difficulty'] as String,
      imageUrl: json['image_url'] as String?,
      description: json['description'] as String?,
      rating: (json['rating'] as num?)?.toDouble(),
      servings: json['servings'] as int?,
      tags: json['tags'] != null 
          ? List<String>.from(json['tags'] as List)
          : null,
    );
  }

  /// Convert to JSON (cho API request)
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'calories': calories,
      'ingredients': ingredients,
      'cooking_time': cookingTime,
      'difficulty': difficulty,
      'image_url': imageUrl,
      'description': description,
      'rating': rating,
      'servings': servings,
      'tags': tags,
    };
  }
}

