"""
Google Gemini API Service
Migrated from React app: chefai/services/geminiService.ts
"""
import os
import json
from typing import List
import google.generativeai as genai
from app.models.recipe import Recipe

# Load API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Recipe schema for structured output (matching React app)
RECIPE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "The name of the dish."},
        "description": {"type": "string", "description": "A tempting short description."},
        "cookTime": {"type": "string", "description": "Total cooking time (e.g., '30 mins')."},
        "difficulty": {
            "type": "string",
            "enum": ["Easy", "Medium", "Hard"],
            "description": "Recipe difficulty level"
        },
        "calories": {"type": "number", "description": "Approximate calories per serving."},
        "ingredients": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of ingredients with measurements."
        },
        "instructions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Step-by-step cooking instructions."
        }
    },
    "required": ["title", "description", "cookTime", "difficulty", "calories", "ingredients", "instructions"]
}

async def generate_recipe(ingredients: List[str]) -> Recipe:
    """
    Generate a recipe using Google Gemini API
    
    Args:
        ingredients: List of available ingredients
        
    Returns:
        Recipe object with generated recipe data
        
    Raises:
        ValueError: If API key is missing or API call fails
    """
    if not ingredients:
        raise ValueError("At least one ingredient is required")
    
    # Initialize model
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": RECIPE_SCHEMA,
            "temperature": 0.7,
        },
        system_instruction=(
            "You are a world-class chef assistant. "
            "You create mouth-watering, easy-to-follow recipes based on limited ingredients."
        )
    )
    
    # Create prompt
    prompt = f"""
    I have the following ingredients in my fridge: {', '.join(ingredients)}.
    
    Please create a delicious, creative, and practical recipe using some or all of these ingredients. 
    You may assume I have basic pantry staples like salt, pepper, oil, and water.
    
    The recipe should be formatted perfectly for a cooking app.
    """
    
    try:
        # Generate content
        response = model.generate_content(prompt)
        
        # Parse JSON response
        if not response.text:
            raise ValueError("No response from Gemini API")
        
        recipe_data = json.loads(response.text)
        
        # Validate and return Recipe model
        return Recipe(**recipe_data)
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Gemini API response: {e}")
    except Exception as e:
        raise ValueError(f"Error generating recipe: {str(e)}")

