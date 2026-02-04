# Architecture

## Overview
This project is a small, production‑ready REST API for managing recipes, built with FastAPI, SQLAlchemy, and SQLite. It is organized in a classic layered style:

- **API layer (FastAPI)**: Request/response handling, input validation, and routing.
- **Service/CRUD layer**: Encapsulates database access logic and filtering behavior.
- **Data layer (SQLAlchemy ORM + SQLite)**: Persistence, schema definition, and relationships.
- **Tests**: Unit tests for CRUD logic and integration tests for the HTTP API.

## Components

### FastAPI Application (`app/main.py`)
- Creates the FastAPI app with title, description, and version.
- Defines dependency `get_db()` that provides a SQLAlchemy Session per request.
- Registers a `startup` event:
  - Initializes the database schema.
  - Seeds a fixed set of sample recipes **only if** the `recipes` table is empty.
- Exposes the following endpoints:
  - `POST /recipes/` – Create a recipe
  - `GET /recipes/{id}` – Fetch a recipe by ID
  - `GET /recipes/` – List **all** recipes (no pagination parameters)
  - `PUT /recipes/{id}` – Update a recipe
  - `DELETE /recipes/{id}` – Delete a recipe
  - `GET /recipes/filter/` – Filter recipes by multiple criteria

The API documentation is auto‑generated via FastAPI’s built‑in OpenAPI support and is available at `/docs`.

### Data Models (`app/models.py`)
- Uses SQLAlchemy ORM and `declarative_base()`.
- Entities:
  - `Recipe`
    - `id: int (PK)`
    - `name: str`
    - `instructions: Text`
    - `vegetarian: bool`
    - `servings: int`
    - Relationship: `ingredients: List[Ingredient]` (many‑to‑many)
  - `Ingredient`
    - `id: int (PK)`
    - `name: str (unique)`
    - Relationship: `recipes: List[Recipe]` (many‑to‑many)
- Many‑to‑many association table `recipe_ingredient` joins recipes and ingredients.

### Database Setup (`app/database.py`)
- Uses SQLite with the URL `sqlite:///./recipes.db`.
- Defines a shared `engine` and `SessionLocal` (non‑autocommit, non‑autoflush).
- `init_db()` creates all tables based on the SQLAlchemy models.

### Schemas / DTOs (`app/schemas.py`)
- Uses Pydantic models to define request/response schemas and validation rules.
- `RecipeBase` defines core fields with constraints:
  - `name`: non‑empty, max length 100.
  - `instructions`: non‑empty, max length 4000.
  - `vegetarian`: bool.
  - `servings`: positive integer, `1–20`.
  - `ingredients`: list of non‑empty ingredient names.
- `RecipeCreate` extends `RecipeBase` without extra fields.
- `RecipeUpdate` allows partial updates with the same constraints when fields are supplied.
- `Ingredient` and `Recipe` schemas are configured with `orm_mode` (Pydantic v1 style) for ORM compatibility.

### CRUD and Filtering Logic (`app/crud.py`)
- Encapsulates all database access:
  - Creates and retrieves `Ingredient` rows, reusing them by name.
  - Creates, reads, updates, and deletes `Recipe` entities.
  - Manages the many‑to‑many relationship by mapping ingredient name lists to `Ingredient` rows.
- `filter_recipes` supports combined filters:
  - `vegetarian` flag.
  - Exact `servings` count.
  - `include_ingredients`: recipes must contain at least one of these ingredients.
  - `exclude_ingredients`: recipes must **not** contain any of these ingredients.
  - `instruction_search`: case‑insensitive substring match over instructions.

### Sample Data (`app/sample_data.py`)
- Contains a curated list of 7 sample recipes with realistic ingredients and instructions.
- On application startup, if there are no recipes in the DB, these recipes are inserted using the same `RecipeCreate` validation and CRUD path as normal API clients.

## Validation & Error Handling

### Request Body Validation
- Implemented primarily via Pydantic schemas in `app/schemas.py`.
- Enforces:
  - Non‑empty names and instructions.
  - Valid servings range.
  - Non‑empty ingredient strings.
- Any invalid payload results in a `422 Unprocessable Entity` with details.

### Path and Query Parameter Validation
- `recipe_id` path parameter uses FastAPI’s `Path` with `gt=0`.
- `GET /recipes/filter/` query validation:
  - `servings`: `0–20`, must be non‑negative.
  - `include_ingredients` / `exclude_ingredients`: non‑empty strings when present.
  - `instruction_search`: 1–200 characters.
  - At least one filter parameter must be provided; otherwise, a `400` is returned.
  - Include and exclude ingredient lists may not overlap; if they do, a `400` is returned.
  - All ingredient and instruction search strings are normalized to lowercase for case‑insensitive matching.

### Error Handling
- 404 for missing recipes on `GET`, `PUT`, and `DELETE`.
- 400 for invalid filter usage (no filters / conflicting include/exclude).
- 422 for schema validation errors.

## Testing Strategy

- **Unit tests** (`tests/test_crud.py`):
  - Use an isolated SQLite test DB (`test.db`).
  - Test creation, retrieval, update, deletion, and filtering logic directly at the CRUD layer.

- **Integration tests** (`tests/test_api.py`):
  - Use `TestClient` from FastAPI.
  - Initialize a clean DB state before the module’s tests.
  - Exercise the real HTTP endpoints: create, read, update, delete, and filtering scenarios.

This separation ensures that both the core business logic and the full HTTP stack (routing, validation, serialization) are covered.

## Rationale / Design Choices

- **FastAPI** for:
  - Modern async‑ready API framework.
  - Built‑in OpenAPI and automatic docs.
  - First‑class validation via Pydantic.
- **SQLite** for simplicity and portability in an assessment setting.
  - Can be swapped for Postgres/MySQL by changing the connection URL and dependencies.
- **SQLAlchemy ORM** for:
  - Clear schema definition in Python.
  - Rich query capabilities, including relationship filtering.
- **Layered structure** (`main` → `crud` → `models`/`database`) keeps concerns separated and makes the code easier to maintain and extend.
