from flask_login import UserMixin, LoginManager
from passlib.apps import custom_app_context as pwd_context
import psycopg2

login_manager = LoginManager()


class User(UserMixin):
    def __init__(self,name,surname,email, username, password):
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

def get_user(user_id):
    statement = """SELECT * FROM Users WHERE username = '%s'""" % (user_id,)
    with psycopg2.connect(database="recipe", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
        with connection.cursor() as cursor:
            cursor.execute(statement)
            user = cursor.fetchall()
            if user is not None:
                for row in user:
                    user = User(row[1], row[2], row[3], row[4], row[5])
                    return user
            else:
                return None
# def hashing(password):
#     secret_key = 'helloworld'
#     return pwd_context.encrypt(password)