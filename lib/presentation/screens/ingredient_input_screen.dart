import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import '../../core/theme/app_theme.dart';

/// Ingredient Input Screen
/// Migrated from chefai/components/IngredientInput.tsx
class IngredientInputScreen extends StatefulWidget {
  const IngredientInputScreen({super.key});

  @override
  State<IngredientInputScreen> createState() => _IngredientInputScreenState();
}

class _IngredientInputScreenState extends State<IngredientInputScreen> {
  final List<String> _ingredients = [];
  final TextEditingController _controller = TextEditingController();
  
  static const List<String> _commonIngredients = [
    "Chicken Breast", "Eggs", "Pasta", "Tomato", "Onion", 
    "Garlic", "Spinach", "Rice", "Milk", "Cheese", "Lemon", "Potato"
  ];

  void _addIngredient(String name) {
    if (name.trim().isEmpty) return;
    
    final trimmed = name.trim();
    if (_ingredients.any((i) => i.toLowerCase() == trimmed.toLowerCase())) {
      _controller.clear();
      return;
    }
    
    setState(() {
      _ingredients.add(trimmed);
      _controller.clear();
    });
  }

  void _removeIngredient(String ingredient) {
    setState(() {
      _ingredients.remove(ingredient);
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          // Header
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  IconButton(
                    icon: const Icon(MdiIcons.arrowBack),
                    onPressed: () => Navigator.pop(context),
                  ),
                  const Expanded(
                    child: Text(
                      'My Fridge',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                  ),
                  const SizedBox(width: 48),
                ],
              ),
            ),
          ),
          
          // Content
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'What\'s inside?',
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Add 3+ ingredients for the best result.',
                    style: TextStyle(
                      fontSize: 15,
                      color: AppTheme.textSecondary,
                    ),
                  ),
                  const SizedBox(height: 24),
                  
                  // Input Field
                  TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: 'e.g., Avocado, Chicken...',
                      hintStyle: TextStyle(
                        color: AppTheme.textSecondary.withOpacity(0.3),
                      ),
                      filled: true,
                      fillColor: AppTheme.surfaceDark,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                      suffixIcon: _controller.text.isNotEmpty
                          ? IconButton(
                              icon: const Icon(MdiIcons.plus),
                              onPressed: () => _addIngredient(_controller.text),
                            )
                          : null,
                    ),
                    style: const TextStyle(
                      fontSize: 18,
                      color: AppTheme.textPrimary,
                    ),
                    onSubmitted: _addIngredient,
                  ),
                  const SizedBox(height: 24),
                  
                  // Selected Ingredients
                  if (_ingredients.isEmpty)
                    Center(
                      child: Column(
                        children: [
                          Icon(
                            MdiIcons.fridge,
                            size: 64,
                            color: AppTheme.textSecondary.withOpacity(0.3),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'Your fridge is empty',
                            style: TextStyle(
                              color: AppTheme.textSecondary.withOpacity(0.3),
                            ),
                          ),
                        ],
                      ),
                    )
                  else
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: _ingredients.map((ingredient) {
                        return Chip(
                          label: Text(ingredient),
                          deleteIcon: const Icon(MdiIcons.close, size: 18),
                          onDeleted: () => _removeIngredient(ingredient),
                          backgroundColor: AppTheme.primaryColor.withOpacity(0.2),
                          labelStyle: const TextStyle(
                            color: AppTheme.textPrimary,
                          ),
                        );
                      }).toList(),
                    ),
                  
                  // Suggestions
                  if (_ingredients.length < 5) ...[
                    const SizedBox(height: 32),
                    Text(
                      'POPULAR ITEMS',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: AppTheme.textSecondary,
                        letterSpacing: 1.2,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: _commonIngredients
                          .where((item) => !_ingredients
                              .any((i) => i.toLowerCase() == item.toLowerCase()))
                          .take(8)
                          .map((item) {
                        return ActionChip(
                          label: Text('+ $item'),
                          onPressed: () => _addIngredient(item),
                          backgroundColor: AppTheme.surfaceDark,
                          labelStyle: const TextStyle(
                            fontSize: 14,
                            color: AppTheme.textPrimary,
                          ),
                        );
                      }).toList(),
                    ),
                  ],
                ],
              ),
            ),
          ),
          
          // Generate Button
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton.icon(
                  onPressed: _ingredients.isEmpty
                      ? null
                      : () {
                          // TODO: Navigate to loading screen and call API
                        },
                  icon: const Icon(MdiIcons.autoAwesome),
                  label: const Text(
                    'Generate Recipe',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

