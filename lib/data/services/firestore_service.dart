import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_core/firebase_core.dart';
import '../models/recipe_model.dart';
import '../../core/constants/app_constants.dart';

/// Firestore Service - Handles all Firestore operations
class FirestoreService {
  static final FirestoreService _instance = FirestoreService._internal();
  factory FirestoreService() => _instance;
  FirestoreService._internal();

  FirebaseFirestore? _firestore;

  /// Initialize Firestore connection
  /// Must be called after Firebase.initializeApp()
  Future<void> initialize() async {
    try {
      _firestore = FirebaseFirestore.instance;
      // Enable offline persistence
      _firestore?.settings = const Settings(
        persistenceEnabled: true,
        cacheSizeBytes: Settings.CACHE_SIZE_UNLIMITED,
      );
    } catch (e) {
      throw Exception('Failed to initialize Firestore: $e');
    }
  }

  /// Get Firestore instance
  FirebaseFirestore get firestore {
    if (_firestore == null) {
      throw Exception('Firestore not initialized. Call initialize() first.');
    }
    return _firestore!;
  }

  /// Check if Firestore is initialized
  bool get isInitialized => _firestore != null;

  /// Get recipes collection reference
  CollectionReference<Map<String, dynamic>> get recipesCollection {
    return firestore.collection(AppConstants.recipesCollection);
  }

  /// Get user favorites collection reference
  CollectionReference<Map<String, dynamic>> get userFavoritesCollection {
    return firestore.collection(AppConstants.userFavoritesCollection);
  }
}

