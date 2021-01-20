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
from recipe import Recipe,Recipe_with_id,get_recipe_id
from wtforms import Form, BooleanField, StringField, PasswordField, validators,SubmitField,TextAreaField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired
from comments import Comment
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

def return_recipe(user_id1):
        with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
            cursor = connection.cursor()
            qSelect = "SELECT * FROM RECIPES WHERE USER_ID = %s"
            cursor.execute(qSelect, (user_id1,))
            results = cursor.fetchall()
            dict_res = []
            for row in results:
                recipe = Recipe_with_id(row[0],row[2],row[3],row[4],row[1])
                dict_res.append(recipe)
            return dict_res

def hashing(password):
    secret_key = 'helloworld'
    return pwd_context.encrypt(password)

@app.route("/")
def home_page():
	return render_template("home.html")

@app.route("/search")
def search_page():
    return render_template("search.html")


@app.route("/recipes/<id>",methods=['GET','POST'])
def recipe_detail_page(id):
    comments = get_comment_for_recipe(id)
    recipe1 = get_recipe_id(id)
    puan = [1,2,3,4,5]
    if request.method=='GET':
        return render_template("recipe_detail.html",recipe=recipe1,comments=comments,recipe_id=id,puan=puan)

    get_comment = request.form['user_comment']
    rate = request.form['user_rate']
    print(get_comment)
    print(rate)
    if get_comment:
        user_id = getuser_id(current_user.username)
        comment = Comment(user_id, id, get_comment, rate)
        add_comment(comment)
        return redirect('/')



def add_comment(comments):
    with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
        cursor = connection.cursor()
        query2 = """INSERT INTO COMMENTS (USER_ID, RECIPE_ID, COMMENT, RATE) VALUES (%s, %s, %s, %s)"""
        cursor.execute(query2, (comments.user_id, comments.recipe_id, comments.comment, comments.rate))
        connection.commit()



def get_comment_for_recipe(recipe_id):
    with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
        cursor = connection.cursor()
        query = "SELECT COMMENT_ID, USER_ID, COMMENT, RATE FROM COMMENTS INNER JOIN USERS ON COMMENTS.USER_ID = USERS.ID WHERE RECIPE_ID = %s ORDER BY COMMENT_ID DESC"
        cursor.execute(query, (recipe_id,))
        comments = cursor.fetchall()
        return comments



@app.route("/myaccount",methods=['GET','POST'])
def profil_page():
    if not current_user.is_authenticated:
        return redirect("/")
    user = """select * from users where username = '%s'""" % (current_user.username,)
    with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
        with connection.cursor() as cursor:
            cursor.execute(user)
            user = cursor.fetchone()[0]
            statement = """SELECT * FROM USERS WHERE ID = (SELECT id FROM USERS WHERE username = '%s')""" \
            % (current_user.username,)
            cursor.execute(statement)
            for row in cursor.fetchall():
                name = row[1]
                surname = row[2]
                email = row[4]
            user_id = getuser_id(current_user)
            result = return_recipe(user_id)
            return render_template("profil.html",
                                    username=current_user.username,name=name, surname=surname,
                                    email=email,result=result)
            abort(404)


def insert_user(user):
        with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
            cursor = connection.cursor()
            query2 = """INSERT INTO USERS (NAME, SURNAME, USERNAME, PASSWORD, EMAIL ) VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query2, (user.name, user.surname, user.username, user.password, user.email))
            connection.commit()
            cursor.close()


def is_exist_recipes():
        with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
            cursor = connection.cursor()
            qSelect = "SELECT NAME FROM RECIPES"
            cursor.execute(qSelect)
            results = cursor.fetchall()
            names = []
            for row in results:
                names.append(row[0])
                print(names)
            return names


class UserRecipeForm(FlaskForm):
    name = StringField('Tarif Adı', validators=[DataRequired()])
    ingredients = StringField('İçindekiler', validators=[DataRequired()])
    instructions = TextAreaField('Yapılışı', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/userRecipe', methods=['GET', 'POST'])
def add_user_recipe():
    form = UserRecipeForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            category = request.form['recipes']
            name = request.form['name']
            ingredients = request.form['ingredients']
            instructions = request.form['instructions']
            all_recipes = is_exist_recipes()

            for key in all_recipes:
                if key == name:
                        categories = ['Kahvaltı','Soğuk','Sıcak','Tatlı']
                        return render_template('user_recipe.html', title='Kendi Tarifinizi Ekleyin', form=form,categories = categories)
            recipe = Recipe(name=name, ingredients=ingredients, instructions=instructions, add_by=current_user)
            insert_recipe(recipe,category)
        return redirect('/myaccount')
    else:
        categories = ['Kahvaltı','Soğuk','Sıcak','Tatlı']
        return render_template('user_recipe.html', title='Kendi Tarifinizi Ekleyin', form=form,categories = categories)

def getuser_id(user):
        with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM USERS WHERE ID = (SELECT id FROM Users WHERE username = '%s')""" \
            % (current_user.username,)
            cursor.execute(statement)
            return_id = cursor.fetchone()[0]
            return return_id

def insert_recipe(recipe,category):
        with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
            cursor = connection.cursor()
            query2 = """INSERT INTO RECIPES ( USER_ID, NAME, INGREDIENTS, CONTENT) VALUES (%s,%s, %s, %s)"""
            statement = """SELECT * FROM USERS WHERE ID = (SELECT id FROM Users WHERE username = '%s')""" \
            % (recipe.add_by.username,)
            cursor.execute(statement)
            return_id = cursor.fetchone()[0]
            cursor.execute(query2, (return_id,recipe.name, recipe.ingredients, recipe.instructions))
            connection.commit()
            insert_recipe_category(recipe,category)
            cursor.close()


def insert_recipe_category(recipe,category):
        with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
            cursor = connection.cursor() 
            query = """INSERT INTO RECIPE_CATEGORY ( RECIPE_ID, CATEGORY_ID) VALUES (%s,%s)"""

            statement = """SELECT * FROM RECIPES WHERE ID = (SELECT id FROM RECIPES WHERE name = '%s')""" \
            % (recipe.name,)
            cursor.execute(statement)
            recipe_id = cursor.fetchone()[0]

            statement2 = """SELECT * FROM CATEGORY WHERE ID = (SELECT id FROM CATEGORY WHERE name = '%s')""" \
            % (category,)
            cursor.execute(statement2)
            category_id = cursor.fetchone()[0]

            cursor.execute(query, (recipe_id,category_id))
            connection.commit()
            cursor.close()





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
        with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
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
        with dbapi2.connect(database="recipe2", user = "postgres", password = "1573596248", host = "127.0.0.1", port = "5432") as connection:
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
                flash(f"Giriş yaptınız.",'success')
                return redirect(url_for('home_page'))
            else:
                flash(f"Kullanıcı adı veya şifre yanlış",'danger')
                return redirect(url_for('login_page'))
        else:
            flash(f"Kullanıcı bulunamadı.",'danger')
            return redirect(url_for('login_page'))
    else:
        return render_template('login.html')


@login_required
@app.route("/logout")
def logout_page():
    if not current_user.is_authenticated:
        return redirect(url_for('login_page'))
    logout_user()
    return redirect(url_for('login_page'))
    




@app.route("/register",methods=['GET','POST'])
def register_page():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        user = User(request.form['name'], request.form['surname'], request.form['username'], request.form['password'], request.form['email'])
        # print("is aut : ",current_user.is_authenticated)
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
