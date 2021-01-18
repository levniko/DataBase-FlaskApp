import os
import sys
import psycopg2 as dbapi2

INIT_STATEMENTS = [
        """
        CREATE TABLE IF NOT EXISTS USERS (
                                 ID SERIAL PRIMARY KEY,
                                 NAME VARCHAR(80) NOT NULL,
                                 SURNAME VARCHAR(80) NOT NULL,
                                 USERNAME VARCHAR(80) NOT NULL,
                                 EMAIL VARCHAR(80) NOT NULL,
                                 PASSWORD VARCHAR(200) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS RECIPES(
                                 ID SERIAL PRIMARY KEY,
                                 USER_ID INTEGER REFERENCES USERS(ID) ON DELETE CASCADE, 
                                 NAME VARCHAR(80) NOT NULL,
                                 PHOTO VARCHAR(80),
                                 CONTENT VARCHAR(255) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS COMMENTS(
                                 ID SERIAL PRIMARY KEY,
                                 USER_ID INTEGER REFERENCES USERS(ID) ON DELETE CASCADE,
                                 RECIPE_ID INTEGER REFERENCES RECIPES(ID) ON DELETE CASCADE,
                                 COMMENT VARCHAR(255) NOT NULL,
                                 RATE INT DEFAULT 0 NOT NULL                                
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS MEMBER(
                                 USER_ID INTEGER REFERENCES USERS(ID) ON DELETE CASCADE
        )
        """,
        # """
        # CREATE TABLE IF NOT EXISTS RECIPE_MATERIALS(
        #                          INGREDIENTS_ID INTEGER REFERENCES INGREDIENTS(ID) ,
        #                          RECIPE_ID INTEGER REFERENCES RECIPES(ID) ON DELETE CASCADE
        # )
        # """,                     
        """CREATE TABLE IF NOT EXISTS INGREDIENTS(
                                 ID SERIAL PRIMARY KEY,
                                 NAME VARCHAR(80) NOT NULL
        )
        """,                   
        """
        CREATE TABLE IF NOT EXISTS CATEGORY(
                                 ID SERIAL PRIMARY KEY,
                                 NAME VARCHAR(80)
        )
        """                          

]


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cursor.close()


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL = url python dbinit.py")
        sys.exit(1)
    initialize(url)