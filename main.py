import json
import sqlite3
from fastapi import FastAPI, HTTPException
from recipes.db import db, to_dict

# RECIPES
from recipes.model import Recipe
from recipes.routes import get_recipes
from recipes.routes import get_recipe_by_id
from recipes.routes import create_recipe
from recipes.routes import delete_recipe_by_id
from recipes.routes import edit_recipe_by_id

# USERS

app = FastAPI()
app.include_router(get_recipes.router)
app.include_router(get_recipe_by_id.router)
app.include_router(create_recipe.router)
app.include_router(delete_recipe_by_id.router)
