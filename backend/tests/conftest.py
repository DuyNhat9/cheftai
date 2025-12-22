"""
Pytest configuration and shared fixtures for CheftAi Backend tests
"""

import pytest
from typing import Dict, Any
import json


@pytest.fixture(scope="session")
def test_config():
    """Test configuration"""
    return {
        "gemini_api_key": "test_key",
        "firestore_project": "cheftai-test",
        "test_timeout": 5.0
    }


@pytest.fixture
def sample_recipe_data():
    """Sample recipe data matching schema"""
    return {
        "id": "test_recipe_001",
        "name": "Test Recipe",
        "calories": 300,
        "ingredients": ["ingredient1", "ingredient2"],
        "cooking_time": 30,
        "difficulty": "Medium",
        "instructions": ["Step 1", "Step 2"]
    }

