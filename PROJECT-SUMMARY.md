# Project Summary

## Goal
Build a standalone, production‑ready Python REST API to manage favourite recipes with:

- Full CRUD operations (add, update, delete, fetch).
- Advanced filtering of recipes by:
  - Vegetarian flag.
  - Servings.
  - Included ingredients.
  - Excluded ingredients.
  - Text search within instructions.
- Persistent storage in a database.
- API documentation.
- Unit and integration tests.

## Technology Stack

- **Language**: Python 3.12
- **Framework**: FastAPI
- **Database**: SQLite (via SQLAlchemy ORM)
- **Validation**: Pydantic models
- **Server (dev)**: Uvicorn
- **Testing**: pytest, FastAPI TestClient

## Key Features

- **Recipe CRUD**
  - `POST /recipes/` – create a new recipe with name, instructions, vegetarian flag, servings, and ingredient list.
  - `GET /recipes/{id}` – fetch a single recipe by ID.
  - `GET /recipes/` – list all recipes.
  - `PUT /recipes/{id}` – update any subset of recipe fields.
  - `DELETE /recipes/{id}` – remove a recipe.

- **Filtering** (`GET /recipes/filter/`)
  - Filter by:
    - `vegetarian` (true/false).
    - `servings` (non‑negative, up to 20).
    - `include_ingredients` – ingredients that must appear.
    - `exclude_ingredients` – ingredients that must not appear.
    - `instruction_search` – case‑insensitive substring search over instructions.
  - Safeguards:
    - At least one filter must be supplied; otherwise a `400` is returned.
    - The same ingredient cannot appear in both include and exclude lists.

- **Sample Data Seeding**
  - On application startup, if no recipes exist in the DB, a fixed set of 7 sample recipes is inserted.
  - Seeding uses the same validation and CRUD path as client requests.

## Data Model (Conceptual)

- **Recipe**
  - `id`: integer, primary key
  - `name`: string
  - `instructions`: text
  - `vegetarian`: boolean
  - `servings`: integer
  - `ingredients`: many‑to‑many relationship with `Ingredient`

- **Ingredient**
  - `id`: integer, primary key
  - `name`: unique string
  - `recipes`: many‑to‑many relationship with `Recipe`

## Validation & API Robustness

- Request bodies (create/update recipes) are validated with Pydantic for:
  - Non‑empty names and instructions.
  - Valid servings range (1–20 on create; same constraint on update when provided).
  - Non‑empty ingredient names.
- Path parameters (recipe IDs) must be positive integers.
- Filter query parameters are strongly validated and normalized to lowercase for case‑insensitive behavior.
- Errors:
  - `404` for missing recipes.
  - `400` for invalid filter usage.
  - `422` for schema/validation issues.

## Testing

- **Unit Tests** (`tests/test_crud.py`)
  - Validate CRUD operations and filter behavior directly on the data/CRUD layer.

- **Integration Tests** (`tests/test_api.py`)
  - Use FastAPI’s TestClient to call the HTTP endpoints.
  - Verify end‑to‑end behavior: status codes, JSON structures, and filtering scenarios.

## How to Run

From the project root:

```bash
pip install -r requirements.txt
.venv/Scripts/Activate.ps1  # on Windows PowerShell
uvicorn app.main:app --reload
```

- API base URL: `http://127.0.0.1:8000`
- Interactive docs: `http://127.0.0.1:8000/docs`

## Deliverable

This repository provides a complete, self‑contained recipe management API that meets the assessment requirements:

- FastAPI‑based REST service.
- Database persistence.
- Documented API (OpenAPI/Swagger).
- Sample data seeding.
- Unit and integration tests.
- Clear architectural and project documentation (`architecture.md`, `PROJECT-SUMMARY.md`, and `README.md`).
