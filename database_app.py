import psycopg2 as dbapi2
from user import User
class store():
    def get_user(self,conf, username):
        with dbapi2.connect(database="recipe", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
            cursor = connection.cursor()
            query = "SELECT NAME, SURNAME, USERNAME, EMAIL, PASSWORD FROM USERS WHERE USERNAME = %s"
            cursor.execute(query, (username,))
            for row in cursor:
                (name, surname, nickname, email, password) = row
                return User(name, surname, nickname, email, password)
                