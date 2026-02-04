from typing import List, Optional
from pydantic import BaseModel, constr, conint

class IngredientBase(BaseModel):
    name: str

class IngredientCreate(IngredientBase):
    pass

class Ingredient(IngredientBase):
    id: int
    class Config:
        orm_mode = True

class RecipeBase(BaseModel):
    # Basic validation for core recipe attributes
    name: constr(min_length=1, max_length=100)
    instructions: constr(min_length=1, max_length=4000)
    vegetarian: bool
    servings: conint(gt=0, le=20)
    ingredients: List[constr(min_length=1, max_length=100)]

class RecipeCreate(RecipeBase):
    pass

class RecipeUpdate(BaseModel):
    # Optional fields with same constraints when provided
    name: Optional[constr(min_length=1, max_length=100)] = None
    instructions: Optional[constr(min_length=1, max_length=4000)] = None
    vegetarian: Optional[bool] = None
    servings: Optional[conint(gt=0, le=20)] = None
    ingredients: Optional[List[constr(min_length=1, max_length=100)]] = None

class Recipe(RecipeBase):
    id: int
    ingredients: List[Ingredient]
    class Config:
        orm_mode = True
