from flask_login import UserMixin, LoginManager
from passlib.apps import custom_app_context as pwd_context
import psycopg2 as dbapi2

login_manager = LoginManager()

class Recipe():
    def __init__(self,name,ingredients,instructions, add_by):
        self.name=name
        self.ingredients=ingredients
        self.instructions = instructions
        self.add_by = add_by    

class Recipe_with_id():
    def __init__(self,id,name,ingredients,instructions, add_by):
        self.id = id
        self.name=name
        self.ingredients=ingredients
        self.instructions = instructions
        self.add_by = add_by 


def get_recipe_id(id):
    with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connect:
        with connect.cursor() as cursor:
            query = "SELECT USER_ID, NAME, INGREDIENTS, CONTENT FROM RECIPES WHERE ID = %s"
            cursor.execute(query, (id,))
            add_by, name, ingredients, content = cursor.fetchone()
            return Recipe(name,ingredients,content,add_by)
                
