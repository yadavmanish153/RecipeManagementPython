from sqlalchemy.orm import Session
from app import models, schemas
from typing import List, Optional

def get_ingredient_by_name(db: Session, name: str) -> Optional[models.Ingredient]:
    return db.query(models.Ingredient).filter(models.Ingredient.name == name).first()

def create_ingredient(db: Session, name: str) -> models.Ingredient:
    db_ingredient = models.Ingredient(name=name)
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

def get_or_create_ingredients(db: Session, ingredient_names: List[str]) -> List[models.Ingredient]:
    ingredients = []
    for name in ingredient_names:
        ingredient = get_ingredient_by_name(db, name)
        if not ingredient:
            ingredient = create_ingredient(db, name)
        ingredients.append(ingredient)
    return ingredients

def create_recipe(db: Session, recipe: schemas.RecipeCreate) -> models.Recipe:
    ingredients = get_or_create_ingredients(db, recipe.ingredients)
    db_recipe = models.Recipe(
        name=recipe.name,
        instructions=recipe.instructions,
        vegetarian=recipe.vegetarian,
        servings=recipe.servings,
        ingredients=ingredients
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

def get_recipe(db: Session, recipe_id: int) -> Optional[models.Recipe]:
    return db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

def get_recipes(db: Session, skip: int = 0, limit: int = 100) -> List[models.Recipe]:
    return db.query(models.Recipe).offset(skip).limit(limit).all()

def update_recipe(db: Session, recipe_id: int, recipe_update: schemas.RecipeUpdate) -> Optional[models.Recipe]:
    db_recipe = get_recipe(db, recipe_id)
    if not db_recipe:
        return None
    for field, value in recipe_update.dict(exclude_unset=True).items():
        if field == "ingredients" and value is not None:
            db_recipe.ingredients = get_or_create_ingredients(db, value)
        else:
            setattr(db_recipe, field, value)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

def delete_recipe(db: Session, recipe_id: int) -> bool:
    db_recipe = get_recipe(db, recipe_id)
    if not db_recipe:
        return False
    db.delete(db_recipe)
    db.commit()
    return True

def filter_recipes(
    db: Session,
    vegetarian: Optional[bool] = None,
    servings: Optional[int] = None,
    include_ingredients: Optional[List[str]] = None,
    exclude_ingredients: Optional[List[str]] = None,
    instruction_search: Optional[str] = None
) -> List[models.Recipe]:
    query = db.query(models.Recipe)
    # Exclude recipes with unwanted ingredients first
    if exclude_ingredients:
        excluded_ids = db.query(models.Recipe.id).join(models.Recipe.ingredients).filter(models.Ingredient.name.in_(exclude_ingredients)).all()
        excluded_ids = [rid for (rid,) in excluded_ids]
        if excluded_ids:
            query = query.filter(~models.Recipe.id.in_(excluded_ids))
    if vegetarian is not None:
        query = query.filter(models.Recipe.vegetarian == vegetarian)
    if servings is not None:
        query = query.filter(models.Recipe.servings == servings)
    if include_ingredients:
        query = query.join(models.Recipe.ingredients).filter(models.Ingredient.name.in_(include_ingredients))
    if instruction_search:
        query = query.filter(models.Recipe.instructions.ilike(f"%{instruction_search}%"))
    return query.all()
