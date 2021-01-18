import psycopg2 as dbapi2
from user import User
class store():
    def add_user(self,conf, users):
        with dbapi2.connect(database="recipe", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
            cursor = connection.cursor()
            query2 = """INSERT INTO USERS (NAME, SURNAME, USERNAME, EMAIL, PASSWORD ) VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query2, (users.name, users.surname, users.username, users.email, users.password))
            connection.commit()

    def get_user(self,conf, username):
        with dbapi2.connect(database="recipe", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
            cursor = connection.cursor()
            query = "SELECT NAME, SURNAME, NICKNAME, EMAIL, PASSWORD FROM USERS WHERE USERNAME = %s"
            cursor.execute(query, (username,))
            for row in cursor:
                (name, surname, nickname, email, password) = row
                return User(name, surname, nickname, email, password)
                
    def update_password(self,conf, username, new_password):
        with dbapi2.connect(database="recipe", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
            cursor = connection.cursor()
            query = "UPDATE USERS SET PASSWORD = %s WHERE (USERNAME = %s)"
            cursor.execute(query, (new_password, username))
            connection.commit()    

    def is_exist(self,conf, username):
        with dbapi2.connect(database="recipe", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
            cursor = connection.cursor()
            query = "SELECT PASSWORD FROM USERS WHERE USERNAME = %s"
            cursor.execute(query, (username,))
            for row in cursor:
                (hashed,) = row
                return hashed