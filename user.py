from flask_login import UserMixin, LoginManager
from passlib.apps import custom_app_context as pwd_context
import psycopg2 as dbapi2

login_manager = LoginManager()

class User(UserMixin):
    def __init__(self,name,surname,username, password, email):
        self.name=name
        self.surname=surname
        self.username = username
        self.password = password
        self.email = email        
        self.is_admin = False
        self.authenticated = True

    def get_id(self):
        return self.username
    
    def is_authenticated(self):
        return self.authenticated

    @property
    def is_active(self):
        return True

def get_user_id(username):
    query = """ 
        SELECT * FROM users WHERE username = '%s'
    """ % (username,)
    with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connect:
        with connect.cursor() as cursor:
            cursor.execute(query)
            returned_user = cursor.fetchall()
            if returned_user is not None:
                for row in returned_user:
                    returned_user = User(row[1], row[2], row[3], row[4], row[5])
                    return returned_user
            else:
                return None
