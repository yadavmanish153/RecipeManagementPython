from fastapi import FastAPI, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas, crud, database
from app.sample_data import SAMPLE_RECIPES

app = FastAPI(title="Recipe Management API", description="Manage your favourite recipes.", version="1.0.0")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup():
    """Initialize database and seed sample data on first startup.

    Sample data is inserted only when the recipes table is empty,
    so your own data will not be overwritten on subsequent runs.
    """
    database.init_db()

    db = database.SessionLocal()
    try:
        # Only seed when there are no recipes yet
        if db.query(models.Recipe).count() == 0:
            for sample in SAMPLE_RECIPES:
                recipe_in = schemas.RecipeCreate(
                    name=sample["name"],
                    instructions=sample["instructions"],
                    vegetarian=sample["vegetarian"],
                    servings=sample["servings"],
                    ingredients=sample["ingredients"],
                )
                crud.create_recipe(db, recipe_in)
    finally:
        db.close()

@app.post("/recipes/", response_model=schemas.Recipe, summary="Add a new recipe")
def add_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    return crud.create_recipe(db, recipe)

@app.get("/recipes/{recipe_id}", response_model=schemas.Recipe, summary="Get a recipe by ID")
def get_recipe(
    recipe_id: int = Path(..., gt=0, description="ID of the recipe"),
    db: Session = Depends(get_db),
):
    db_recipe = crud.get_recipe(db, recipe_id)
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return db_recipe

@app.get("/recipes/", response_model=List[schemas.Recipe], summary="List all recipes")
def list_recipes(db: Session = Depends(get_db)):
    """Return all recipes without pagination parameters."""
    return crud.get_recipes(db)

@app.put("/recipes/{recipe_id}", response_model=schemas.Recipe, summary="Update a recipe")
def update_recipe(
    recipe_id: int = Path(..., gt=0, description="ID of the recipe"),
    recipe_update: schemas.RecipeUpdate = ...,
    db: Session = Depends(get_db),
):
    db_recipe = crud.update_recipe(db, recipe_id, recipe_update)
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return db_recipe

@app.delete("/recipes/{recipe_id}", summary="Delete a recipe")
def delete_recipe(
    recipe_id: int = Path(..., gt=0, description="ID of the recipe"),
    db: Session = Depends(get_db),
):
    success = crud.delete_recipe(db, recipe_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"ok": True}

@app.get("/recipes/filter/", response_model=List[schemas.Recipe], summary="Filter recipes")
def filter_recipes(
    vegetarian: Optional[bool] = Query(None, description="Filter by vegetarian flag"),
    servings: Optional[int] = Query(None, ge=0, le=20, description="Exact number of servings (non-negative)"),
    include_ingredients: Optional[List[str]] = Query(None, min_length=1, description="Ingredients that must be present"),
    exclude_ingredients: Optional[List[str]] = Query(None, min_length=1, description="Ingredients that must NOT be present"),
    instruction_search: Optional[str] = Query(None, min_length=1, max_length=200, description="Text to search in instructions"),
    db: Session = Depends(get_db)
):
    # Normalize string filters to lowercase for case-insensitive matching
    norm_include = [i.lower() for i in include_ingredients] if include_ingredients else None
    norm_exclude = [i.lower() for i in exclude_ingredients] if exclude_ingredients else None
    norm_instruction = instruction_search.lower() if instruction_search else None
    # Require at least one filtering criterion to avoid unbounded queries
    if (
        vegetarian is None
        and servings is None
        and not norm_include
        and not norm_exclude
        and norm_instruction is None
    ):
        raise HTTPException(
            status_code=400,
            detail="At least one filter parameter must be provided.",
        )

    # include_ingredients and exclude_ingredients must not contain the same item
    if norm_include and norm_exclude:
        overlap = set(norm_include) & set(norm_exclude)
        if overlap:
            raise HTTPException(
                status_code=400,
                detail=f"Ingredients cannot be both included and excluded: {sorted(overlap)}",
            )
    return crud.filter_recipes(
        db,
        vegetarian=vegetarian,
        servings=servings,
        include_ingredients=norm_include,
        exclude_ingredients=norm_exclude,
        instruction_search=norm_instruction,
    )
