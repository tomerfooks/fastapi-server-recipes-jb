from fastapi import APIRouter

from recipes.db import db, to_dict

router = APIRouter()

@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int):
    conn = db()
    try:
        conn.execute(f"DELETE FROM recipes WHERE id = '{recipe_id}'")
    finally:
        conn.close()
    return f"Recipe id {recipe_id} was deleted successfully"
    