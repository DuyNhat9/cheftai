import 'package:flutter/material.dart';
import '../../domain/entities/recipe.dart';

/// RecipeCard Widget - Hiển thị một recipe trong danh sách
/// Material Design 3 với dark mode
class RecipeCard extends StatelessWidget {
  final Recipe recipe;
  final VoidCallback? onTap;
  final VoidCallback? onFavorite;

  const RecipeCard({
    Key? key,
    required this.recipe,
    this.onTap,
    this.onFavorite,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Recipe Image
            _buildImage(colorScheme),
            
            // Recipe Info
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Title and Favorite
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: Text(
                          recipe.name,
                          style: theme.textTheme.titleLarge,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.favorite_border),
                        onPressed: onFavorite,
                        iconSize: 24,
                        color: colorScheme.primary,
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 8),
                  
                  // Description (if available)
                  if (recipe.description != null)
                    Text(
                      recipe.description!,
                      style: theme.textTheme.bodyMedium,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  
                  const SizedBox(height: 12),
                  
                  // Recipe Meta Info
                  Row(
                    children: [
                      _buildMetaChip(
                        context,
                        Icons.local_fire_department,
                        '${recipe.calories} cal',
                        colorScheme,
                      ),
                      const SizedBox(width: 8),
                      _buildMetaChip(
                        context,
                        Icons.timer,
                        '${recipe.cookingTime} min',
                        colorScheme,
                      ),
                      const SizedBox(width: 8),
                      _buildMetaChip(
                        context,
                        Icons.restaurant,
                        recipe.difficulty,
                        colorScheme,
                      ),
                    ],
                  ),
                  
                  // Rating (if available)
                  if (recipe.rating != null) ...[
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Icon(
                          Icons.star,
                          size: 16,
                          color: colorScheme.tertiary,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          recipe.rating!.toStringAsFixed(1),
                          style: theme.textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ],
                  
                  // Tags (if available)
                  if (recipe.tags != null && recipe.tags!.isNotEmpty) ...[
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 6,
                      runSpacing: 6,
                      children: recipe.tags!.take(3).map((tag) {
                        return Chip(
                          label: Text(
                            tag,
                            style: TextStyle(
                              fontSize: 11,
                              color: colorScheme.primary,
                            ),
                          ),
                          backgroundColor: colorScheme.primaryContainer,
                          padding: const EdgeInsets.symmetric(horizontal: 4),
                          materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        );
                      }).toList(),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildImage(ColorScheme colorScheme) {
    return AspectRatio(
      aspectRatio: 16 / 9,
      child: recipe.imageUrl != null
          ? Image.network(
              recipe.imageUrl!,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) {
                return _buildPlaceholderImage(colorScheme);
              },
              loadingBuilder: (context, child, loadingProgress) {
                if (loadingProgress == null) return child;
                return Center(
                  child: CircularProgressIndicator(
                    value: loadingProgress.expectedTotalBytes != null
                        ? loadingProgress.cumulativeBytesLoaded /
                            loadingProgress.expectedTotalBytes!
                        : null,
                  ),
                );
              },
            )
          : _buildPlaceholderImage(colorScheme),
    );
  }

  Widget _buildPlaceholderImage(ColorScheme colorScheme) {
    return Container(
      color: colorScheme.surfaceVariant,
      child: Center(
        child: Icon(
          Icons.restaurant_menu,
          size: 64,
          color: colorScheme.onSurfaceVariant,
        ),
      ),
    );
  }

  Widget _buildMetaChip(
    BuildContext context,
    IconData icon,
    String label,
    ColorScheme colorScheme,
  ) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: colorScheme.surfaceVariant,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: colorScheme.onSurfaceVariant),
          const SizedBox(width: 4),
          Text(
            label,
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }
}

