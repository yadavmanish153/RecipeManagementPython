import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app import schemas, database, models
import app.crud

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_db():
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    models.Base.metadata.drop_all(bind=engine)

def test_create_and_get_recipe(test_db):
    recipe_in = schemas.RecipeCreate(
        name="Veggie Pizza",
        instructions="Bake in oven.",
        vegetarian=True,
        servings=2,
        ingredients=["cheese", "tomato", "dough"]
    )
    recipe = app.crud.create_recipe(test_db, recipe_in)
    assert recipe.name == "Veggie Pizza"
    fetched = app.crud.get_recipe(test_db, recipe.id)
    assert fetched.id == recipe.id
    assert fetched.vegetarian is True
    assert "cheese" in [i.name for i in fetched.ingredients]

def test_update_recipe(test_db):
    recipe_in = schemas.RecipeCreate(
        name="Salmon Bake",
        instructions="Bake salmon in oven.",
        vegetarian=False,
        servings=4,
        ingredients=["salmon", "lemon"]
    )
    recipe = app.crud.create_recipe(test_db, recipe_in)
    update = schemas.RecipeUpdate(servings=6)
    updated = app.crud.update_recipe(test_db, recipe.id, update)
    assert updated.servings == 6

def test_delete_recipe(test_db):
    recipe_in = schemas.RecipeCreate(
        name="Temp",
        instructions="Temp instructions.",
        vegetarian=False,
        servings=1,
        ingredients=["temp"]
    )
    recipe = app.crud.create_recipe(test_db, recipe_in)
    assert app.crud.delete_recipe(test_db, recipe.id) is True
    assert app.crud.get_recipe(test_db, recipe.id) is None

def test_filter_recipes(test_db):
    # Add recipes
    app.crud.create_recipe(test_db, schemas.RecipeCreate(
        name="Potato Stew",
        instructions="Cook potatoes.",
        vegetarian=True,
        servings=4,
        ingredients=["potatoes", "carrot"]
    ))
    app.crud.create_recipe(test_db, schemas.RecipeCreate(
        name="Salmon Pie",
        instructions="Bake salmon in oven.",
        vegetarian=False,
        servings=4,
        ingredients=["salmon", "potatoes"]
    ))
    # Vegetarian filter
    veg = app.crud.filter_recipes(test_db, vegetarian=True)
    assert all(r.vegetarian for r in veg)
    # Servings and ingredient
    filtered = app.crud.filter_recipes(test_db, servings=4, include_ingredients=["potatoes"])
    assert any("potatoes" in [i.name for i in r.ingredients] for r in filtered)
    # Exclude ingredient and instruction search
    filtered2 = app.crud.filter_recipes(test_db, exclude_ingredients=["salmon"], instruction_search="oven")
    assert all("salmon" not in [i.name for i in r.ingredients] for r in filtered2)
    assert all("oven" in r.instructions for r in filtered2)
