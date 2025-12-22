import 'package:flutter/material.dart';
import '../../domain/entities/recipe.dart';
import '../widgets/recipe_card.dart';

/// RecipeResultScreen - Hiển thị kết quả tìm kiếm công thức
/// Migrated từ React component RecipeResult.tsx
/// Sử dụng Material Design 3 với Dark Mode
class RecipeResultScreen extends StatefulWidget {
  final List<Recipe> recipes;
  final String? searchQuery;
  final VoidCallback? onRefresh;

  const RecipeResultScreen({
    Key? key,
    required this.recipes,
    this.searchQuery,
    this.onRefresh,
  }) : super(key: key);

  @override
  State<RecipeResultScreen> createState() => _RecipeResultScreenState();
}

class _RecipeResultScreenState extends State<RecipeResultScreen> {
  String _sortBy = 'relevance'; // relevance, calories, time, rating
  String? _filterDifficulty;
  int? _maxCalories;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    // Filter và sort recipes
    List<Recipe> filteredRecipes = _getFilteredAndSortedRecipes();

    return Scaffold(
      appBar: AppBar(
        title: widget.searchQuery != null
            ? Text('Results for "${widget.searchQuery}"')
            : const Text('Recipe Results'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _showFilterDialog,
            tooltip: 'Filter',
          ),
          IconButton(
            icon: const Icon(Icons.sort),
            onPressed: _showSortDialog,
            tooltip: 'Sort',
          ),
          if (widget.onRefresh != null)
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: widget.onRefresh,
              tooltip: 'Refresh',
            ),
        ],
      ),
      body: _buildBody(filteredRecipes, colorScheme, theme),
    );
  }

  Widget _buildBody(
    List<Recipe> recipes,
    ColorScheme colorScheme,
    ThemeData theme,
  ) {
    if (recipes.isEmpty) {
      return _buildEmptyState(colorScheme, theme);
    }

    return CustomScrollView(
      slivers: [
        // Results count header
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: [
                Text(
                  '${recipes.length} recipe${recipes.length != 1 ? 's' : ''} found',
                  style: theme.textTheme.bodyMedium,
                ),
                const Spacer(),
                if (_hasActiveFilters())
                  Chip(
                    label: const Text('Filters active'),
                    onDeleted: _clearFilters,
                    backgroundColor: colorScheme.surfaceVariant,
                    deleteIcon: const Icon(Icons.close, size: 18),
                  ),
              ],
            ),
          ),
        ),

        // Recipe list
        SliverPadding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0),
          sliver: SliverList(
            delegate: SliverChildBuilderDelegate(
              (context, index) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 16.0),
                  child: RecipeCard(
                    recipe: recipes[index],
                    onTap: () => _navigateToRecipeDetail(recipes[index]),
                  ),
                );
              },
              childCount: recipes.length,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyState(ColorScheme colorScheme, ThemeData theme) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.restaurant_menu,
            size: 80,
            color: colorScheme.onSurfaceVariant,
          ),
          const SizedBox(height: 24),
          Text(
            'No recipes found',
            style: theme.textTheme.headlineMedium,
          ),
          const SizedBox(height: 8),
          Text(
            widget.searchQuery != null
                ? 'Try adjusting your search or filters'
                : 'Start searching for recipes',
            style: theme.textTheme.bodyMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          if (_hasActiveFilters())
            ElevatedButton.icon(
              onPressed: _clearFilters,
              icon: const Icon(Icons.clear_all),
              label: const Text('Clear Filters'),
            ),
        ],
      ),
    );
  }

  List<Recipe> _getFilteredAndSortedRecipes() {
    List<Recipe> filtered = List.from(widget.recipes);

    // Apply filters
    if (_filterDifficulty != null) {
      filtered = filtered
          .where((r) => r.difficulty.toLowerCase() == _filterDifficulty!.toLowerCase())
          .toList();
    }

    if (_maxCalories != null) {
      filtered = filtered.where((r) => r.calories <= _maxCalories!).toList();
    }

    // Apply sorting
    switch (_sortBy) {
      case 'calories':
        filtered.sort((a, b) => a.calories.compareTo(b.calories));
        break;
      case 'time':
        filtered.sort((a, b) => a.cookingTime.compareTo(b.cookingTime));
        break;
      case 'rating':
        filtered.sort((a, b) {
          final aRating = a.rating ?? 0.0;
          final bRating = b.rating ?? 0.0;
          return bRating.compareTo(aRating);
        });
        break;
      case 'relevance':
      default:
        // Keep original order (relevance from API)
        break;
    }

    return filtered;
  }

  bool _hasActiveFilters() {
    return _filterDifficulty != null || _maxCalories != null;
  }

  void _clearFilters() {
    setState(() {
      _filterDifficulty = null;
      _maxCalories = null;
    });
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) => _FilterDialog(
        currentDifficulty: _filterDifficulty,
        currentMaxCalories: _maxCalories,
        onApply: (difficulty, maxCalories) {
          setState(() {
            _filterDifficulty = difficulty;
            _maxCalories = maxCalories;
          });
          Navigator.of(context).pop();
        },
        onClear: () {
          _clearFilters();
          Navigator.of(context).pop();
        },
      ),
    );
  }

  void _showSortDialog() {
    showDialog(
      context: context,
      builder: (context) => _SortDialog(
        currentSort: _sortBy,
        onSelect: (sortBy) {
          setState(() {
            _sortBy = sortBy;
          });
          Navigator.of(context).pop();
        },
      ),
    );
  }

  void _navigateToRecipeDetail(Recipe recipe) {
    // TODO: Navigate to recipe detail screen
    // Navigator.push(
    //   context,
    //   MaterialPageRoute(
    //     builder: (context) => RecipeDetailScreen(recipe: recipe),
    //   ),
    // );
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Opening ${recipe.name}...'),
        duration: const Duration(seconds: 1),
      ),
    );
  }
}

/// Filter Dialog
class _FilterDialog extends StatefulWidget {
  final String? currentDifficulty;
  final int? currentMaxCalories;
  final Function(String?, int?) onApply;
  final VoidCallback onClear;

  const _FilterDialog({
    required this.currentDifficulty,
    required this.currentMaxCalories,
    required this.onApply,
    required this.onClear,
  });

  @override
  State<_FilterDialog> createState() => _FilterDialogState();
}

class _FilterDialogState extends State<_FilterDialog> {
  String? _selectedDifficulty;
  int? _maxCalories;

  @override
  void initState() {
    super.initState();
    _selectedDifficulty = widget.currentDifficulty;
    _maxCalories = widget.currentMaxCalories;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return AlertDialog(
      title: const Text('Filter Recipes'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Difficulty', style: theme.textTheme.titleMedium),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: ['Easy', 'Medium', 'Hard'].map((difficulty) {
              final isSelected = _selectedDifficulty == difficulty;
              return FilterChip(
                label: Text(difficulty),
                selected: isSelected,
                onSelected: (selected) {
                  setState(() {
                    _selectedDifficulty = selected ? difficulty : null;
                  });
                },
              );
            }).toList(),
          ),
          const SizedBox(height: 24),
          Text('Max Calories', style: theme.textTheme.titleMedium),
          const SizedBox(height: 8),
          Slider(
            value: _maxCalories?.toDouble() ?? 1000,
            min: 100,
            max: 2000,
            divisions: 19,
            label: _maxCalories != null ? '${_maxCalories} cal' : 'No limit',
            onChanged: (value) {
              setState(() {
                _maxCalories = value.toInt();
              });
            },
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              TextButton(
                onPressed: () {
                  setState(() {
                    _maxCalories = null;
                  });
                },
                child: const Text('No limit'),
              ),
              Text('${_maxCalories ?? 1000} cal'),
            ],
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: widget.onClear,
          child: const Text('Clear All'),
        ),
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () => widget.onApply(_selectedDifficulty, _maxCalories),
          child: const Text('Apply'),
        ),
      ],
    );
  }
}

/// Sort Dialog
class _SortDialog extends StatelessWidget {
  final String currentSort;
  final Function(String) onSelect;

  const _SortDialog({
    required this.currentSort,
    required this.onSelect,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final options = [
      {'value': 'relevance', 'label': 'Relevance', 'icon': Icons.star},
      {'value': 'rating', 'label': 'Highest Rated', 'icon': Icons.thumb_up},
      {'value': 'calories', 'label': 'Lowest Calories', 'icon': Icons.local_fire_department},
      {'value': 'time', 'label': 'Quickest', 'icon': Icons.timer},
    ];

    return AlertDialog(
      title: const Text('Sort By'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: options.map((option) {
          final isSelected = currentSort == option['value'];
          return RadioListTile<String>(
            title: Text(option['label'] as String),
            leading: Icon(option['icon'] as IconData),
            value: option['value'] as String,
            groupValue: currentSort,
            onChanged: (value) {
              if (value != null) {
                onSelect(value);
              }
            },
          );
        }).toList(),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Close'),
        ),
      ],
    );
  }
}

