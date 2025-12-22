"""
Pydantic models for Recipe data structure
Based on React app types and Gemini API response schema
"""
from pydantic import BaseModel, Field
from typing import List, Literal

class RecipeRequest(BaseModel):
    """Request model for recipe generation"""
    ingredients: List[str] = Field(
        ...,
        min_items=1,
        description="List of ingredients available"
    )

class Recipe(BaseModel):
    """Recipe response model matching React app types"""
    title: str = Field(..., description="The name of the dish")
    description: str = Field(..., description="A tempting short description")
    cookTime: str = Field(..., description="Total cooking time (e.g., '30 mins')")
    difficulty: Literal["Easy", "Medium", "Hard"] = Field(
        ...,
        description="Recipe difficulty level"
    )
    calories: int = Field(..., ge=0, description="Approximate calories per serving")
    ingredients: List[str] = Field(
        ...,
        description="List of ingredients with measurements"
    )
    instructions: List[str] = Field(
        ...,
        description="Step-by-step cooking instructions"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Spicy Basil Chicken",
                "description": "A flavorful Thai-inspired dish",
                "cookTime": "25 mins",
                "difficulty": "Medium",
                "calories": 450,
                "ingredients": [
                    "2 chicken breasts",
                    "1 cup fresh basil",
                    "2 tbsp soy sauce"
                ],
                "instructions": [
                    "Cut chicken into bite-sized pieces",
                    "Heat oil in a pan",
                    "Cook chicken until golden"
                ]
            }
        }

