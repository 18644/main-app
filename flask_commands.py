from flask import Flask,g,render_template,request,redirect,url_for,flash,session
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import sqlite3
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

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#The home page, displays the 'franchise' table.
@app.route("/")
def home():
    if 'username' in session:
        results = f'Logged in as {session["username"]}'
        return render_template("home.html", result=results)
    else:
        return redirect(url_for('login'))

@app.route("/franchise")
def franchise():
    if 'username' in session:
        cursor = get_db().cursor()
        sql = ("SELECT * FROM franchise")
        cursor.execute(sql)
        results = cursor.fetchall()
    else:
        flash('Login first!')
        return redirect(url_for('login'))
    return render_template("franchise.html", name=session.get("username","Unknown"), results=results)

#Allows the chosen description from the franchise table to be displayed by the id.
@app.route("/details/<int:id>")
def details(id):
    if 'username' in session:
        cursor = get_db().cursor()
        description = ("SELECT description FROM franchise WHERE id=?")
        cursor.execute(description,(id,))
        results = cursor.fetchall()
    else:
        flash('Login first!')
        return redirect(url_for('login'))
    return render_template("details.html", results=results)

#Allows the chosen description from the character table to be displayed by its id.
@app.route("/details_characters/<int:id>")
def details_characters(id):
    if 'username' in session:
        cursor = get_db().cursor()
        description = ("SELECT description FROM characters WHERE id=?")
        cursor.execute(description,(id,))
        results = cursor.fetchall()
    else:
        flash('Login first!')
        return redirect(url_for('login'))
    return render_template("details_characters.html", results=results)

@app.route("/characters")
def characters():
    if 'username' in session:
        cursor = get_db().cursor()
        sql = ("SELECT * FROM characters")
        cursor.execute(sql)
        results = cursor.fetchall()
    else:
        flash('Login first!')
        return redirect(url_for('login'))
    return render_template("characters.html", results=results)

@app.route("/searchE", methods=['GET', 'POST'])
def era():
    if 'username' in session:
        cursor = get_db().cursor()
        if request.method == "POST":
            era = request.values['era']
            results = cursor.fetchall()
            if len(results) == 0 and era == 'all':
                sql = ("SELECT year, description from era")
                cursor.execute(sql)
                results = cursor.fetchall()
            else:
                sql = ("SELECT year, description from era WHERE year LIKE ?")
                cursor.execute(sql,(era,))
                results = cursor.fetchall()
            return render_template('searchE.html', results=results)
    else:
        flash('Login first!')
        return redirect(url_for('login'))  
    return render_template('searchE.html')

@app.route('/insertE', methods=['GET', 'POST'])
def insert():
    if 'username' in session:
        cursor = get_db().cursor()
        if request.method == "POST":
            era = request.values['era']
            sql = ("INSERT INTO era (year, description) Values (?)")
            cursor.execute(sql,(era,))
            return redirect("http://localhost:5000/searchE", code=302)
    else:
        flash('Login first!')
        return redirect(url_for('login'))
    return render_template('insertE.html')

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":
        cursor = get_db().cursor()
        user_id = request.form.get("username")
        password = request.form.get("password")

        sql = ("INSERT INTO login(user_id, password) values (?,?)")
        print (user_id + " user") 
        print (password + " pass")
        try:
            cursor.execute(sql,(user_id, password))
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
    return render_template("home.html", results=results)

@app.route('/fail')
def fail():
    return render_template("fail.html")

@app.route('/find', methods=['GET','POST'])
def logging():
    if request.method == "POST":
        cursor = get_db().cursor()
        user_id = request.form.get("username")
        password = request.form.get("password")
        find_user = ("SELECT * FROM login WHERE (user_id,password) = (?,?)")
        cursor.execute(find_user,(user_id, password))
        results = cursor.fetchall()
        print (results)
        if len(results) > 0:
            session['username'] = request.form['username']
            flash ("you have logged in!")
            return redirect ("/login")
            
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)