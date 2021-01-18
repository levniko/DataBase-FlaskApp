import psycopg2 
from flask import Flask, render_template, url_for,request,redirect,flash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from user import User,get_user
from config import config	
from database_app import store
import psycopg2 as dbapi2
from psycopg2 import extensions
import hashlib 
from passlib.hash import sha256_crypt
import datetime
import json
import os
import psycopg2 as dbapi2
import re
from db_init import initialize

app = Flask(__name__)

extensions.register_type(extensions.UNICODE)
extensions.register_type(extensions.UNICODEARRAY)

HEROKU = False

if (not HEROKU):
    os.environ['DATABASE_URL'] = "dbname='recipe2' user = 'postgres' host = 'localhost' password = '1573596248'"
    initialize(os.environ.get('DATABASE_URL'))


def is_exist(username):
    with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
        cursor = connection.cursor()
        query = "SELECT PASSWORD FROM USERS WHERE USERNAME = %s"
        cursor.execute(query, (username,))
        for row in cursor:
            (hashed,) = row
            return hashed

def is_exist_email(email):
    with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
        cursor = connection.cursor()
        query = "SELECT PASSWORD FROM USERS WHERE EMAIL = %s"
        cursor.execute(query, (email,))
        for row in cursor:
            (hashed,) = row
            return hashed


@app.route("/")
def home_page():
	return render_template("home.html")

@app.route("/search")
def search_page():
    return render_template("search.html")

@app.route("/add")
def add_page():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        name = request.form.get('name')
        photo = request.form.get('photo') 
        content = request.form.get('content')

        # if store.is_exist(app.config['dsn'], request.form['username']):
        #     return render_template('register.html', error = "This username is already taken.")
        insert_recipe(name, photo, content)

    return render_template("add_recipe.html")

@app.route("/myaccount")
def account_page():
    return render_template("account.html")
    
@app.route('/login', methods=['GET','POST'])
def login_page():
    if request.method == 'POST':
        username = request.form('username')
        user = get_user(username)
        if user is not None:    
            password = request.form('password')
            password1 = user.password
            if sha256_crypt.verify(password,password1):
                login_user(user)
                flash("You have logged in.")
                return redirect(url_for('home_page'))
            else:
                return redirect(url_for('login_page'))
    else:
        return render_template('login.html')


def hash_password(password):
            return sha256_crypt.hash(password)

def insert_user(name,surname,username,password,email):
        with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
            cursor = connection.cursor()
            query2 = """INSERT INTO USERS (NAME, SURNAME, USERNAME, EMAIL, PASSWORD ) VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query2, (name, surname, username, email, password))
            connection.commit()
            cursor.close()

def insert_recipe(name,photo,content):
        with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
            cursor = connection.cursor()
            query2 = """INSERT INTO RECIPES (NAME, PHOTO, CONTENT) VALUES (%s, %s, %s)"""
            cursor.execute(query2, (name, photo, content))
            connection.commit()
            cursor.close()
          

@app.route("/register",methods=['GET','POST'])
def register_page():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        name = request.form.get('name')
        surname = request.form.get('surname') 
        username = request.form.get('username')
        password = sha256_crypt.hash(request.form.get('password'))
        email = request.form.get('email')
        if is_exist(request.form['username']):
            return render_template('register.html', error = "This username is already taken.")
        elif is_exist_email(request.form['email']):
            return render_template('register.html', error = "This email is already taken.")
        insert_user(name,surname,username,password,email)
        return redirect(url_for('login_page'))



if __name__ =="__main__":
    if not HEROKU:
        app.run(debug = True)
    else:
        app.run()
