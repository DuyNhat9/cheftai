"""
Tests for FastAPI endpoint /api/recipes/generate
Task: T008
Owner: Testing_QA

This module tests the recipe generation endpoint that uses Google Gemini API
to generate recipes based on user-provided ingredients.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any
import json


# Mock FastAPI app structure - adjust import path based on actual structure
# from backend.main import app
# For now, we'll create a test structure that can be adapted

class TestRecipeGenerateEndpoint:
    """Test suite for /api/recipes/generate endpoint"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        # TODO: Import actual app when backend is created
        # from backend.main import app
        # return TestClient(app)
        # For now, return mock client structure
        return Mock()
    
    @pytest.fixture
    def mock_gemini_response(self):
        """Mock successful Gemini API response"""
        return {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps({
                            "name": "Spicy Basil Chicken",
                            "calories": 350,
                            "ingredients": ["chicken", "basil", "garlic", "chili"],
                            "cooking_time": 25,
                            "difficulty": "Medium",
                            "instructions": [
                                "Heat oil in pan",
                                "Cook chicken until golden",
                                "Add basil and spices",
                                "Serve hot"
                            ]
                        })
                    }]
                }
            }]
        }
    
    @pytest.fixture
    def valid_request_data(self):
        """Valid request payload"""
        return {
            "ingredients": ["chicken", "basil", "garlic", "onion"],
            "dietary_preferences": ["none"],
            "servings": 2
        }
    
    # ==================== SUCCESS CASES ====================
    
    def test_generate_recipe_success_basic(self, client, mock_gemini_response, valid_request_data):
        """
        Test successful recipe generation with valid ingredients
        Expected: 200 OK with recipe data
        """
        with patch('backend.services.gemini_service.generate_recipe') as mock_gemini:
            mock_gemini.return_value = mock_gemini_response
            
            response = client.post(
                "/api/recipes/generate",
                json=valid_request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure matches schema
            assert "id" in data
            assert "name" in data
            assert data["name"] == "Spicy Basil Chicken"
            assert "calories" in data
            assert isinstance(data["calories"], int)
            assert data["calories"] == 350
            assert "ingredients" in data
            assert isinstance(data["ingredients"], list)
            assert "cooking_time" in data
            assert isinstance(data["cooking_time"], int)
            assert data["cooking_time"] == 25
            assert "difficulty" in data
            assert data["difficulty"] in ["Easy", "Medium", "Hard"]
            assert "instructions" in data
            assert isinstance(data["instructions"], list)
    
    def test_generate_recipe_success_with_dietary_preferences(self, client, mock_gemini_response):
        """
        Test recipe generation with dietary preferences (vegan, vegetarian, etc.)
        Expected: 200 OK with recipe matching preferences
        """
        request_data = {
            "ingredients": ["tofu", "tomato", "basil"],
            "dietary_preferences": ["vegan"],
            "servings": 2
        }
        
        # Mock vegan-specific response
        vegan_response = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps({
                            "name": "Vegan Basil Tofu",
                            "calories": 280,
                            "ingredients": ["tofu", "tomato", "basil", "olive oil"],
                            "cooking_time": 20,
                            "difficulty": "Easy",
                            "instructions": ["Prepare tofu", "Cook with vegetables"]
                        })
                    }]
                }
            }]
        }
        
        with patch('backend.services.gemini_service.generate_recipe') as mock_gemini:
            mock_gemini.return_value = vegan_response
            
            response = client.post(
                "/api/recipes/generate",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Vegan Basil Tofu"
            assert data["calories"] == 280
    
    def test_generate_recipe_success_minimal_ingredients(self, client, mock_gemini_response):
        """
        Test recipe generation with minimal ingredients (1-2 items)
        Expected: 200 OK, AI should still generate recipe
        """
        request_data = {
            "ingredients": ["chicken"],
            "dietary_preferences": [],
            "servings": 1
        }
        
        with patch('backend.services.gemini_service.generate_recipe') as mock_gemini:
            mock_gemini.return_value = mock_gemini_response
            
            response = client.post(
                "/api/recipes/generate",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "name" in data
            assert "ingredients" in data
    
    def test_generate_recipe_success_custom_servings(self, client, mock_gemini_response):
        """
        Test recipe generation with custom servings
        Expected: 200 OK, recipe should scale ingredients
        """
        request_data = {
            "ingredients": ["chicken", "rice", "vegetables"],
            "dietary_preferences": [],
            "servings": 4
        }
        
        with patch('backend.services.gemini_service.generate_recipe') as mock_gemini:
            mock_gemini.return_value = mock_gemini_response
            
            response = client.post(
                "/api/recipes/generate",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "servings" in data or "ingredients" in data  # Should reflect serving size
    
    # ==================== ERROR CASES ====================
    
    def test_generate_recipe_error_missing_ingredients(self, client):
        """
        Test error when ingredients list is missing
        Expected: 400 Bad Request
        """
        request_data = {
            "dietary_preferences": [],
            "servings": 2
        }
        
        response = client.post(
            "/api/recipes/generate",
            json=request_data
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "detail" in data
        assert "ingredients" in str(data).lower()
    
    def test_generate_recipe_error_empty_ingredients(self, client):
        """
        Test error when ingredients list is empty
        Expected: 400 Bad Request
        """
        request_data = {
            "ingredients": [],
            "dietary_preferences": [],
            "servings": 2
        }
        
        response = client.post(
            "/api/recipes/generate",
            json=request_data
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_generate_recipe_error_invalid_ingredients_type(self, client):
        """
        Test error when ingredients is not a list
        Expected: 422 Unprocessable Entity
        """
        request_data = {
            "ingredients": "chicken, basil",  # Should be list, not string
            "dietary_preferences": [],
            "servings": 2
        }
        
        response = client.post(
            "/api/recipes/generate",
            json=request_data
        )
        
        assert response.status_code == 422  # FastAPI validation error
    
    def test_generate_recipe_error_invalid_servings(self, client):
        """
        Test error when servings is invalid (negative or zero)
        Expected: 400 Bad Request
        """
        request_data = {
            "ingredients": ["chicken", "basil"],
            "dietary_preferences": [],
            "servings": 0  # Invalid
        }
        
        response = client.post(
            "/api/recipes/generate",
            json=request_data
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_generate_recipe_error_gemini_api_failure(self, client):
        """
        Test error when Gemini API fails
        Expected: 503 Service Unavailable or 500 Internal Server Error
        """
        request_data = {
            "ingredients": ["chicken", "basil"],
            "dietary_preferences": [],
            "servings": 2
        }
        
        with patch('backend.services.gemini_service.generate_recipe') as mock_gemini:
            mock_gemini.side_effect = Exception("Gemini API Error: Rate limit exceeded")
            
            response = client.post(
                "/api/recipes/generate",
                json=request_data
            )
            
            assert response.status_code in [500, 503]
            data = response.json()
            assert "error" in data or "detail" in data
    
    def test_generate_recipe_error_gemini_api_timeout(self, client):
        """
        Test error when Gemini API times out
        Expected: 504 Gateway Timeout or 500 Internal Server Error
        """
        request_data = {
            "ingredients": ["chicken", "basil"],
            "dietary_preferences": [],
            "servings": 2
        }
        
        with patch('backend.services.gemini_service.generate_recipe') as mock_gemini:
            import asyncio
            mock_gemini.side_effect = asyncio.TimeoutError("Request timeout")
            
            response = client.post(
                "/api/recipes/generate",
                json=request_data
            )
            
            assert response.status_code in [500, 504]
            data = response.json()
            assert "error" in data or "detail" in data
    
    def test_generate_recipe_error_invalid_json(self, client):
        """
        Test error when request body is invalid JSON
        Expected: 422 Unprocessable Entity
        """
        response = client.post(
            "/api/recipes/generate",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_generate_recipe_error_missing_required_fields(self, client):
        """
        Test error when required fields are missing
        Expected: 422 Unprocessable Entity
        """
        request_data = {}  # Empty request
        
        response = client.post(
            "/api/recipes/generate",
            json=request_data
        )
        
        assert response.status_code == 422
    
    def test_generate_recipe_error_invalid_dietary_preferences(self, client):
        """
        Test error when dietary_preferences contains invalid values
        Expected: 400 Bad Request or 422 Unprocessable Entity
        """
        request_data = {
            "ingredients": ["chicken", "basil"],
            "dietary_preferences": ["invalid_preference"],
            "servings": 2
        }
        
        response = client.post(
            "/api/recipes/generate",
            json=request_data
        )
        
        # Should either accept and ignore invalid, or return error
        assert response.status_code in [200, 400, 422]
    
    def test_generate_recipe_error_gemini_invalid_response_format(self, client):
        """
        Test error when Gemini returns invalid response format
        Expected: 500 Internal Server Error
        """
        request_data = {
            "ingredients": ["chicken", "basil"],
            "dietary_preferences": [],
            "servings": 2
        }
        
        # Mock invalid response (missing required fields)
        invalid_response = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": "Invalid JSON response"
                    }]
                }
            }]
        }
        
        with patch('backend.services.gemini_service.generate_recipe') as mock_gemini:
            mock_gemini.return_value = invalid_response
            
            response = client.post(
                "/api/recipes/generate",
                json=request_data
            )
            
            # Should handle gracefully or return error
            assert response.status_code in [200, 500]
            if response.status_code == 500:
                data = response.json()
                assert "error" in data or "detail" in data
    
    # ==================== EDGE CASES ====================
    
    def test_generate_recipe_edge_case_many_ingredients(self, client, mock_gemini_response):
        """
        Test recipe generation with many ingredients (10+)
        Expected: 200 OK, should handle gracefully
        """
        request_data = {
            "ingredients": ["chicken", "beef", "pork", "fish", "tofu", 
                          "tomato", "onion", "garlic", "basil", "oregano", 
                          "thyme", "rosemary", "pepper", "salt"],
            "dietary_preferences": [],
            "servings": 2
        }
        
        with patch('backend.services.gemini_service.generate_recipe') as mock_gemini:
            mock_gemini.return_value = mock_gemini_response
            
            response = client.post(
                "/api/recipes/generate",
                json=request_data
            )
            
            assert response.status_code == 200
    
    def test_generate_recipe_edge_case_special_characters_in_ingredients(self, client, mock_gemini_response):
        """
        Test recipe generation with special characters in ingredient names
        Expected: 200 OK, should sanitize or handle properly
        """
        request_data = {
            "ingredients": ["chicken (breast)", "basil & thyme", "garlic-chopped"],
            "dietary_preferences": [],
            "servings": 2
        }
        
        with patch('backend.services.gemini_service.generate_recipe') as mock_gemini:
            mock_gemini.return_value = mock_gemini_response
            
            response = client.post(
                "/api/recipes/generate",
                json=request_data
            )
            
            assert response.status_code == 200


# ==================== INTEGRATION TESTS ====================

class TestRecipeGenerateIntegration:
    """Integration tests for recipe generation endpoint"""
    
    @pytest.fixture
    def client(self):
        """Create test client for integration tests"""
        # TODO: Use actual app instance
        return Mock()
    
    @pytest.mark.integration
    def test_generate_recipe_integration_full_flow(self, client):
        """
        Integration test: Full flow from request to response
        Expected: Complete recipe generation workflow
        """
        # This would test the full stack without mocks
        # Requires actual backend setup
        pass
    
    @pytest.mark.integration
    def test_generate_recipe_integration_database_save(self, client):
        """
        Integration test: Verify recipe is saved to database
        Expected: Recipe persisted in Firestore
        """
        # This would test database integration
        # Requires actual Firestore setup
        pass


# ==================== PERFORMANCE TESTS ====================

class TestRecipeGeneratePerformance:
    """Performance tests for recipe generation endpoint"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return Mock()
    
    @pytest.mark.performance
    def test_generate_recipe_performance_response_time(self, client, mock_gemini_response):
        """
        Performance test: Response time should be < 5 seconds
        Expected: Fast response even with AI processing
        """
        import time
        request_data = {
            "ingredients": ["chicken", "basil"],
            "dietary_preferences": [],
            "servings": 2
        }
        
        with patch('backend.services.gemini_service.generate_recipe') as mock_gemini:
            mock_gemini.return_value = mock_gemini_response
            
            start_time = time.time()
            response = client.post(
                "/api/recipes/generate",
                json=request_data
            )
            end_time = time.time()
            
            assert response.status_code == 200
            assert (end_time - start_time) < 5.0  # Should respond in < 5 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

