import pytest
from fastapi.testclient import TestClient
import app.main
from app import models, database

client = TestClient(app.main.app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """Initialize a clean database state for API tests."""
    # Ensure schema exists
    database.init_db()

    # Clear any existing data that may violate current validation rules
    db = database.SessionLocal()
    try:
        db.query(models.Recipe).delete()
        db.query(models.Ingredient).delete()
        db.commit()
    finally:
        db.close()

@pytest.fixture
def recipe_data():
    return {
        "name": "Veggie Soup",
        "instructions": "Boil vegetables.",
        "vegetarian": True,
        "servings": 3,
        "ingredients": ["carrot", "potato"]
    }

def test_add_and_get_recipe(recipe_data):
    response = client.post("/recipes/", json=recipe_data)
    assert response.status_code == 200
    recipe = response.json()
    recipe_id = recipe["id"]
    get_resp = client.get(f"/recipes/{recipe_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == recipe_data["name"]

def test_update_recipe(recipe_data):
    response = client.post("/recipes/", json=recipe_data)
    recipe_id = response.json()["id"]
    update_resp = client.put(f"/recipes/{recipe_id}", json={"servings": 5})
    assert update_resp.status_code == 200
    assert update_resp.json()["servings"] == 5

def test_delete_recipe(recipe_data):
    response = client.post("/recipes/", json=recipe_data)
    recipe_id = response.json()["id"]
    del_resp = client.delete(f"/recipes/{recipe_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["ok"] is True

def test_filter_recipes():
    # Add recipes
    client.post("/recipes/", json={
        "name": "Potato Curry",
        "instructions": "Cook potatoes.",
        "vegetarian": True,
        "servings": 4,
        "ingredients": ["potatoes", "spices"]
    })
    client.post("/recipes/", json={
        "name": "Fish Pie",
        "instructions": "Bake fish in oven.",
        "vegetarian": False,
        "servings": 4,
        "ingredients": ["fish", "potatoes"]
    })
    # Vegetarian filter
    resp = client.get("/recipes/filter/?vegetarian=true")
    assert resp.status_code == 200
    assert all(r["vegetarian"] for r in resp.json())
    # Servings and ingredient
    resp2 = client.get("/recipes/filter/?servings=4&include_ingredients=potatoes")
    assert resp2.status_code == 200
    assert any("potatoes" in [i["name"] for i in r["ingredients"]] for r in resp2.json())
    # Exclude ingredient and instruction search
    resp3 = client.get("/recipes/filter/?exclude_ingredients=fish&instruction_search=oven")
    assert resp3.status_code == 200
    assert all("fish" not in [i["name"] for i in r["ingredients"]] for r in resp3.json())
    assert all("oven" in r["instructions"] for r in resp3.json())
