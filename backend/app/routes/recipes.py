"""
Recipe API Routes
FastAPI endpoints for recipe generation
"""
from fastapi import APIRouter, HTTPException
from app.models.recipe import RecipeRequest, Recipe
from app.services.gemini_service import generate_recipe

router = APIRouter()

@router.post("/recipes/generate", response_model=Recipe)
async def create_recipe(request: RecipeRequest):
    """
    Generate a recipe from available ingredients using AI
    
    Args:
        request: RecipeRequest with list of ingredients
        
    Returns:
        Recipe object with generated recipe
        
    Raises:
        HTTPException: If recipe generation fails
    """
    try:
        recipe = await generate_recipe(request.ingredients)
        return recipe
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/recipes/health")
async def recipes_health():
    """Health check for recipes service"""
    return {"status": "healthy", "service": "recipes"}

