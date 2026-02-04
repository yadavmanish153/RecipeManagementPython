# Recipe Management Python Application

## Overview
A standalone RESTful application for managing favourite recipes, built with FastAPI and SQLite. Users can add, update, remove, fetch, and filter recipes by vegetarian status, servings, ingredients (include/exclude), and text search in instructions.

## Architecture
- **FastAPI**: Web framework for REST API and auto-generated OpenAPI docs.
- **SQLAlchemy**: ORM for database models and queries.
- **SQLite**: Lightweight, file-based database for persistence.
- **Pydantic**: Data validation and serialization.
- **Testing**: Unit tests (business logic) and integration tests (API endpoints) using pytest and httpx.

### Project Structure
- `app/models.py`: SQLAlchemy models for Recipe and Ingredient
- `app/database.py`: Database setup and initialization
- `app/schemas.py`: Pydantic schemas for request/response
- `app/crud.py`: CRUD and filtering logic
- `app/main.py`: FastAPI app and endpoints
- `tests/`: Unit and integration tests

## How to Run
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Start the application**
   ```bash
   .venv\Scripts\Activate.ps1
   uvicorn app.main:app --reload
   ```
   The API will be available at http://127.0.0.1:8000
3. **API Documentation**
   Visit http://127.0.0.1:8000/docs for interactive OpenAPI docs.

## Testing
Run all tests with:
```bash
pytest
```

## Example API Usage
- Add a recipe: `POST /recipes/`
- Get a recipe: `GET /recipes/{id}`
- Update a recipe: `PUT /recipes/{id}`
- Delete a recipe: `DELETE /recipes/{id}`
- List recipes: `GET /recipes/`
- Filter recipes: `GET /recipes/filter/` with query params

## Production Readiness
- Input validation and error handling
- Database transactions
- Modular code structure
- Automated tests

## Deployment
- Can be deployed on any platform supporting Python 3.8+
- For production, use a robust server (e.g., Gunicorn) and configure environment variables for DB path if needed.

---

**Ready for public git hosting.**
