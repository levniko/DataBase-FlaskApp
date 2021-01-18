import psycopg2 
from flask import Flask, render_template, url_for,request,redirect,flash,abort
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from user import User,get_user_id	
from database_app import store
import psycopg2 as dbapi2
from psycopg2 import extensions
import hashlib 
from passlib.hash import pbkdf2_sha256
from passlib.apps import custom_app_context as pwd_context
import datetime
import json
import os
import re
from db_init import initialize

app = Flask(__name__)

app.secret_key = 'xxxxyyyyyzzzzz'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return get_user_id(user_id)

extensions.register_type(extensions.UNICODE)
extensions.register_type(extensions.UNICODEARRAY)

HEROKU = True

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

def hashing(password):
    secret_key = 'helloworld'
    return pwd_context.encrypt(password)

@app.route("/")
def home_page():
	return render_template("home.html")

@app.route("/search")
def search_page():
    return render_template("search.html")

@app.route("/add")
def add_page():
        return render_template('add_recipe.html')


@app.route("/myaccount")
def profil_page():
    if not current_user.is_authenticated:
        return redirect("/")
    user = """select * from users where username = '%s'""" % (current_user.username,)
    with psycopg2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
        with connection.cursor() as cursor:
            cursor.execute(user)
            user = cursor.fetchone()[0]
            statement = """SELECT * FROM USERS WHERE ID = (SELECT id FROM Users WHERE username = '%s')""" \
            % (current_user.username,)
            cursor.execute(statement)
            for row in cursor.fetchall():
                print(row)
                name = row[1]
                surname = row[2]
                email = row[4]
            return render_template("profil.html",
                                    username=current_user.username,name=name, surname=surname,
                                    email=email)
            abort(404)



# @login_required
# @app.route("/update-profile", methods=['GET','POST'])
# def update_profile():
#     if request.method == 'GET':
#         return render_template("update-profile.html")
#     if not current_user.is_authenticated:
#         return redirect("/")
#     query = """SELECT id FROM Users WHERE username = '%s'""" % (current_user.username,)
#     with psycopg2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
#         with connection.cursor() as cursor:
#             cursor.execute(query)
#             for row in cursor.fetchall():
#                 print(row)
#                 user_id = row[0]

#             name = request.form['name']
#             surname = request.form['surname']
#             email = request.form['email']
#             query = """UPDATE USERS SET name = '%s', surname = '%s', email = '%s' WHERE ID = %s""" % (name, surname, email, id)
#             cursor.execute(query)
#             query = """UPDATE Users SET name = '%s', surname = '%s' WHERE id = %s""" % (name, surname, user_id)
#             cursor.execute(query)
#             connection.commit()
#     return redirect("/myaccount")

# @login_required
# @app.route("/addrecipe", methods=['GET','POST'])
# def add_recipe():
#     if request.method == 'GET':
#         return render_template("add_recipe.html")
#     if not current_user.is_authenticated:
#         return redirect("/")
    
@login_required
@app.route("/password", methods=['GET','POST'])
def change_password():
    if request.method == 'GET':
        return render_template("password.html")
    if not current_user.is_authenticated:
        return redirect("/")
    new1 = request.form['new1']
    new2 = request.form['new2']
    if new1 != new2:
        message = "New passwords don't match. Try again."
        return render_template("password.html", message=message)
    old = request.form['old']
    truepassword = is_exist(current_user.username)
    if pwd_context.verify(old, truepassword):
        new = hashing(new1)
        
        query = """UPDATE USERS SET password = '%s' WHERE username = '%s'""" % (new, current_user.username)
        with psycopg2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
               
                logout_user()
                return redirect("/login")
    else:
        message = "The old password you entered is incorrect. Try again."
        return render_template("password.html", message=message)


@login_required
@app.route("/update-profile", methods=['GET','POST'])
def update_profile():
    if request.method == 'GET':
        return render_template("update-profile.html")
    if not current_user.is_authenticated:
        return redirect("/")
    name = request.form['name']
    surname = request.form['surname']
    pass1 = request.form['pass']
    truepassword = is_exist(current_user.username)
    if pwd_context.verify(pass1, truepassword):
        query = """UPDATE USERS SET NAME = '%s',SURNAME = '%s' WHERE username = '%s'""" % (name,surname, current_user.username)
        with psycopg2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                return redirect(url_for('profil_page'))
    else:
        message = "The password you entered is incorrect. Try again."
        return render_template("update-profile.html", message=message)


@app.route('/login', methods=['GET','POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        truepassword = is_exist(username)
        if truepassword:                
            user = get_user_id(username)
            if pwd_context.verify(password, truepassword):
                login_user(user)
                flash("Giriş yaptınız.")
                print(current_user.is_authenticated)
                return redirect(url_for('home_page'))
            else:
                flash("Kullanıcı adı veya şifre yanlış")
                return redirect(url_for('login_page'))
        else:
            flash("Kullanıcı bulunamadı.")
            return redirect(url_for('login_page'))
    else:
        return render_template('login.html')


@login_required
@app.route("/logout")
def logout_page():
    if not current_user.is_authenticated:
        return redirect(url_for('home_page'))
    logout_user()
    return redirect(url_for('home_page'))
    
def insert_user(user):
        with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
            cursor = connection.cursor()
            query2 = """INSERT INTO USERS (NAME, SURNAME, USERNAME, PASSWORD, EMAIL ) VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query2, (user.name, user.surname, user.username, user.password, user.email))
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
        user = User(request.form['name'], request.form['surname'], request.form['username'], request.form['password'], request.form['email'])
        print("is aut : ",current_user.is_authenticated)
        user.password = hashing(user.password)
        if is_exist(request.form['username']):
            return render_template('register.html', error = "Kullanıcı adı alınmış.")

        if is_exist_email(request.form['email']):
            return render_template('register.html', error = "Bu email ile kayıt olunmuş.")

        insert_user(user)        
        return redirect(url_for('login_page'))


if __name__ =="__main__":
    if not HEROKU:
        app.run(debug = True)
    else:
        app.run()
