# CheftAi Backend - FastAPI

Backend API server for CheftAi Android app using FastAPI and Google Gemini API.

## 🚀 Setup

### Prerequisites
- Python 3.10+
- pip

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup environment variables:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

4. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### POST `/api/recipes/generate`
Generate a recipe from ingredients.

**Request:**
```json
{
  "ingredients": ["chicken", "tomato", "onion"]
}
```

**Response:**
```json
{
  "title": "Spicy Basil Chicken",
  "description": "A flavorful Thai-inspired dish",
  "cookTime": "25 mins",
  "difficulty": "Medium",
  "calories": 450,
  "ingredients": ["2 chicken breasts", "1 cup fresh basil"],
  "instructions": ["Cut chicken...", "Heat oil..."]
}
```

### GET `/health`
Health check endpoint.

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── routes/
│   │   └── recipes.py       # Recipe API endpoints
│   ├── services/
│   │   └── gemini_service.py # Gemini API integration
│   └── models/
│       └── recipe.py        # Pydantic models
├── tests/                   # Unit tests
├── requirements.txt         # Python dependencies
└── README.md
```

## 🧪 Testing

```bash
pytest tests/
```

## 📝 Notes

- API key is stored in environment variables (not in code)
- CORS is enabled for Flutter app development
- Structured output from Gemini API using JSON schema

