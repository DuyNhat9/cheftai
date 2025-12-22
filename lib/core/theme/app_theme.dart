import 'package:flutter/material.dart';

/// Material Design 3 Theme cho CheftAi Android
/// Dark Mode với Material You (Dynamic Color)
class AppTheme {
  // Material You Color Scheme - Dark Mode
  static const ColorScheme _darkColorScheme = ColorScheme(
    brightness: Brightness.dark,
    primary: Color(0xFFFF6B35), // Orange accent cho food theme
    onPrimary: Color(0xFFFFFFFF),
    secondary: Color(0xFF4ECDC4), // Teal accent
    onSecondary: Color(0xFF000000),
    tertiary: Color(0xFFFFE66D), // Yellow accent
    onTertiary: Color(0xFF000000),
    error: Color(0xFFFF5252),
    onError: Color(0xFFFFFFFF),
    surface: Color(0xFF1E1E1E), // Dark surface
    onSurface: Color(0xFFE0E0E0),
    surfaceVariant: Color(0xFF2C2C2C),
    onSurfaceVariant: Color(0xFFB0B0B0),
    outline: Color(0xFF5C5C5C),
    shadow: Color(0xFF000000),
  );

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: _darkColorScheme,
      scaffoldBackgroundColor: _darkColorScheme.surface,
      
      // AppBar Theme
      appBarTheme: AppBarTheme(
        backgroundColor: _darkColorScheme.surface,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          color: _darkColorScheme.onSurface,
          fontSize: 20,
          fontWeight: FontWeight.w600,
        ),
        iconTheme: IconThemeData(
          color: _darkColorScheme.onSurface,
        ),
      ),

      // Card Theme
      cardTheme: CardTheme(
        color: _darkColorScheme.surfaceVariant,
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
      ),

      // Text Theme
      textTheme: TextTheme(
        displayLarge: TextStyle(
          color: _darkColorScheme.onSurface,
          fontSize: 32,
          fontWeight: FontWeight.bold,
        ),
        displayMedium: TextStyle(
          color: _darkColorScheme.onSurface,
          fontSize: 28,
          fontWeight: FontWeight.bold,
        ),
        headlineMedium: TextStyle(
          color: _darkColorScheme.onSurface,
          fontSize: 24,
          fontWeight: FontWeight.w600,
        ),
        titleLarge: TextStyle(
          color: _darkColorScheme.onSurface,
          fontSize: 20,
          fontWeight: FontWeight.w600,
        ),
        bodyLarge: TextStyle(
          color: _darkColorScheme.onSurface,
          fontSize: 16,
        ),
        bodyMedium: TextStyle(
          color: _darkColorScheme.onSurfaceVariant,
          fontSize: 14,
        ),
        labelLarge: TextStyle(
          color: _darkColorScheme.primary,
          fontSize: 14,
          fontWeight: FontWeight.w500,
        ),
      ),

      // Elevated Button Theme
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: _darkColorScheme.primary,
          foregroundColor: _darkColorScheme.onPrimary,
          elevation: 2,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),

      // Icon Theme
      iconTheme: IconThemeData(
        color: _darkColorScheme.onSurfaceVariant,
        size: 24,
      ),
    );
  }
}

