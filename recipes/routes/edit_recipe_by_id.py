from fastapi import APIRouter

from recipes.db import db, to_dict

router = APIRouter()

@app.put("/recipes/{recipe_id}")
def edit_recipe_by_id(recipe: Recipe, recipe_id: int):
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
    
