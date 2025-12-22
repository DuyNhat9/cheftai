import 'package:flutter/material.dart';
import 'core/theme/app_theme.dart';
import 'presentation/screens/recipe_result_screen.dart';
import 'domain/entities/recipe.dart';

void main() {
  runApp(const CheftAiApp());
}

class CheftAiApp extends StatelessWidget {
  const CheftAiApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CheftAi',
      theme: AppTheme.darkTheme,
      debugShowCheckedModeBanner: false,
      home: const RecipeResultScreenDemo(),
    );
  }
}

/// Demo Screen để test RecipeResultScreen
class RecipeResultScreenDemo extends StatelessWidget {
  const RecipeResultScreenDemo({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Sample recipes for demo
    final sampleRecipes = [
      Recipe(
        id: '1',
        name: 'Spicy Basil Chicken',
        calories: 450,
        ingredients: ['Chicken', 'Basil', 'Chili', 'Garlic'],
        cookingTime: 25,
        difficulty: 'Medium',
        imageUrl: null,
        description: 'Aromatic Thai-style stir-fry with fresh basil',
        rating: 4.5,
        servings: 2,
        tags: ['Thai', 'Spicy', 'Quick & Easy'],
      ),
      Recipe(
        id: '2',
        name: 'Fluffy Pancakes',
        calories: 320,
        ingredients: ['Flour', 'Eggs', 'Milk', 'Butter'],
        cookingTime: 15,
        difficulty: 'Easy',
        imageUrl: null,
        description: 'Light and airy pancakes perfect for breakfast',
        rating: 4.8,
        servings: 4,
        tags: ['Breakfast', 'Sweet'],
      ),
      Recipe(
        id: '3',
        name: 'Ultimate Grilled Cheese',
        calories: 580,
        ingredients: ['Bread', 'Cheese', 'Butter'],
        cookingTime: 10,
        difficulty: 'Easy',
        imageUrl: null,
        description: 'Classic comfort food with crispy golden bread',
        rating: 4.2,
        servings: 1,
        tags: ['Comfort Food', 'Quick & Easy'],
      ),
      Recipe(
        id: '4',
        name: 'Pasta Carbonara',
        calories: 650,
        ingredients: ['Pasta', 'Eggs', 'Bacon', 'Parmesan'],
        cookingTime: 20,
        difficulty: 'Medium',
        imageUrl: null,
        description: 'Creamy Italian pasta with crispy bacon',
        rating: 4.7,
        servings: 2,
        tags: ['Italian', 'Comfort Food'],
      ),
    ];

    return RecipeResultScreen(
      recipes: sampleRecipes,
      searchQuery: 'chicken',
      onRefresh: () {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Refreshing recipes...')),
        );
      },
    );
  }
}

