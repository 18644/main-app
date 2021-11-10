from flask import Flask,g,render_template,request,redirect,url_for,flash,session
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
DATABASE = 'characters.db'
app.secret_key = b'_5#y2L"F4Q8z\n\xeb]/'

#This connects the database to the website, allowing display of things within the database.
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def set_password(self, password):
        self.password_hash = generate_password_hash(password)

def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#The home page, ensures the user is logged in.
@app.route("/")
def home():
    if 'username' in session:
        results = f'Logged in as {session["username"]}'
        return render_template("home.html", result=results)
    else:
        flash("You have been redirected to the home page. please log in first to access this page!")
        return redirect(url_for('login'))

#displays the franchise table, only if the user is logged in.
@app.route("/franchise")
def franchise():
    if 'username' in session:
        cursor = get_db().cursor()
        sql = ("SELECT * FROM franchise")
        cursor.execute(sql)
        results = cursor.fetchall()
    else:
        flash('You have been redirected to the home page. please log in first to access this page!')
        return redirect(url_for('login'))
    return render_template("franchise.html", name=session.get("username","Unknown"), results=results)

#Allows the chosen description from the franchise table to be displayed by the id. This only happens if the user is logged in.
@app.route("/details/<int:id>")
def details(id):
    if 'username' in session:
        cursor = get_db().cursor()
        description = ("SELECT description FROM franchise WHERE id=?")
        cursor.execute(description,(id,))
        results = cursor.fetchall()
    else:
        flash('You have been redirected to the home page. please log in first to access this page!')
        return redirect(url_for('login'))
    return render_template("details.html", results=results)

#Displays the character table, only if the user is logged in.
@app.route("/characters")
def characters():
    if 'username' in session:
        cursor = get_db().cursor()
        sql = ("SELECT * FROM characters")
        cursor.execute(sql)
        results = cursor.fetchall()
    else:
        flash('You have been redirected to the home page. please log in first to access this page!')
        return redirect(url_for('login'))
    return render_template("characters.html", results=results)


#Allows the chosen description from the character table to be displayed by its id. This only happens if the user is logged in.
@app.route("/details_characters/<int:id>")
def details_characters(id):
    if 'username' in session:
        cursor = get_db().cursor()
        description = ("SELECT description FROM characters WHERE id=?")
        cursor.execute(description,(id,))
        results = cursor.fetchall()
    else:
        flash('You have been redirected to the home page. please log in first to access this page!')
        return redirect(url_for('login'))
    return render_template("details_characters.html", results=results)

#This allows the user to search for a particular year by a search bar. This is only if the user is logged in.
@app.route("/searchE", methods=['GET', 'POST'])
def era():
    if 'username' in session:
        cursor = get_db().cursor()
        if request.method == "POST":
            era = request.values['era']
            results = cursor.fetchall()
            if len(results) == 0:
                flash("Nothing found, please try again.")
            else:
                sql = ("SELECT year, description from era WHERE year LIKE ?")
                cursor.execute(sql,(era,))
                results = cursor.fetchall()
            return render_template('searchE.html', results=results)
    else:
        flash('You have been redirected to the home page. please log in first to access this page!')
        return redirect(url_for('login'))  
    return render_template('searchE.html')

#This allows the information the user is asked for from the era table to be displayed. 
#if found, the data is displayed. If not, the page redirectes for the user to search again. This only happens if the user is logged in.
@app.route('/insertE', methods=['GET', 'POST'])
def insert():
    if 'username' in session:
        cursor = get_db().cursor()
        if request.method == "POST":
            era = request.values['era']
            sql = ("INSERT INTO era (year) Values (?)")
            if len(sql) == 0:
                flash("Nothing found, please try again.")
                return redirect('searchE.html')
            else:
                cursor.execute(sql,(era,))
                results = cursor.fetchall()
                return redirect('searchE.html')
            return render_template('insertE.html', results=results)
    else:
        flash('You have been redirected to the home page. please log in first to access this page!')
        return redirect(url_for('login'))
    return render_template('insertE.html')


@app.route('/login')
def login():
    return render_template("login.html")

#This page allows for the user to create their own username and password. It does not allow for two users to have the same username.
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":
        cursor = get_db().cursor()
        user_id = request.form.get("username")
        password = request.form.get("password")
        password_hash = generate_password_hash(password)
        sql = ("INSERT INTO login(user_id, password) values (?,?)")
        print (user_id + "user") 
        print (password + "pass")
        try:
            cursor.execute(sql,(user_id, password_hash))
            cursor = get_db().commit()
            flash ("Welcome!")
        except:
            flash ("this username already exists!")
        return redirect ("/register")
    return render_template("register.html")

@app.route('/logged')
def logged():
    home()
    cursor = get_db().cursor()
    sql = ("SELECT * FROM login WHERE user_id = (?)")
    cursor.execute(sql,(session['username'],))
    results = cursor.fetchall()
    print(results)

@app.route('/fail')
def fail():
    return render_template("fail.html")

#This page allows for the user to log in if they already have a username and password. This page will also appear if the user trys to access a page when they have not yet logged in.
@app.route('/find', methods=['GET','POST'])
def logging():
    if request.method == "POST":
        cursor = get_db().cursor()
        user_id = request.form.get("username")
        password = request.form.get("password")
        password_hash = generate_password_hash(password)
        find_user = ("SELECT * FROM login WHERE (user_id,password) = (?,?)")
        cursor.execute(find_user,(user_id, password_hash))
        results = cursor.fetchall()
        print (results)
        if check_password_hash(password_hash, password):
            session['username'] = request.form['username']
            flash ("you have logged in!")
            return redirect ("/")
        else:
            flash("Incorrect username and or password. Please try again.")
            return redirect ("/login")

#allows the user to log out and clear their cookies.
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
