import json
import sqlite3
from fastapi import FastAPI, HTTPException

from recipes.db import db, to_dict
from recipes.model import Recipe
from recipes.routes import get_recipes

app = FastAPI()
app.include_router(get_recipes.router)

@app.get("/recipes/{recipe_id}")
def get_recipe_by_id(recipe_id: int):
    conn = db()
    try:
        row = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Recipe not found")
        return to_dict(row)
    finally:
        conn.close()

@app.post("/recipes", status_code=201)
def create_recipe(recipe: Recipe):
    data = recipe.model_dump()
    for c in ("ingredients", "instructions"):
        data[c] = json.dumps(data[c])
    conn = db()
    try:
        with conn:  # commits on success, rolls back on exception
            cur = conn.execute(
                f"INSERT INTO recipes ({', '.join(data)}) "
                f"VALUES ({', '.join('?' * len(data))})",
                list(data.values()),
            )
    except sqlite3.IntegrityError as e:
        raise HTTPException(400, str(e))
    finally:
        conn.close()
    return {"id": cur.lastrowid, **recipe.model_dump()}

@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int):
    conn = db()
    try:
        conn.execute(f"DELETE FROM recipes WHERE id = '{recipe_id}'")
    finally:
        conn.close()
    return f"Recipe id {recipe_id} was deleted successfully"
    
@app.put("/recipes/{recipe_id}")
def edit_recipe(recipe: Recipe, recipe_id: int):
    conn = db()
    data = recipe.model_dump()
    for c in ("ingredients", "instructions"):
        data[c] = json.dumps(data[c])
    conn = db()
    try:
        with conn:  # commits on success, rolls back on exception
            cur = conn.execute(
                f"UPDATE recipes SET name = '{recipe.name}', cook_time_minutes = {recipe.cook_time_minutes}, servings = {recipe.servings}, difficulty = '{recipe.difficulty}', calories_per_serving = {recipe.calories_per_serving}, user_id = {recipe.user_id}, ingredients = '{data["ingredients"]}', instructions = '{data["instructions"]}' WHERE id = {recipe_id};"
            )
    except sqlite3.IntegrityError as e:
        raise HTTPException(400, str(e))
    finally:
        conn.close()
    return data
    
