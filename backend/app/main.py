"""
CheftAi Backend - FastAPI Application
Main entry point for the API server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import recipes, agents

app = FastAPI(
    title="CheftAi API",
    description="AI-Powered Recipe App Backend",
    version="0.1.0"
)

# CORS middleware for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recipes.router, prefix="/api", tags=["recipes"])
app.include_router(agents.router, prefix="/api", tags=["agents"])

@app.get("/")
async def root():
    return {
        "message": "CheftAi API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

