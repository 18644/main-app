from flask import Flask,g,render_template,request,redirect,url_for
import sqlite3


app = Flask(__name__)

DATABASE = 'characters.db'

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

@app.route("/")
def home():
    cursor = get_db().cursor()
    sql = ("SELECT * FROM franchise")
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("franchise.html", results=results)

@app.route("/characters")
def characters():
    cursor = get_db().cursor()
    sql = ("SELECT name,description FROM characters")
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("characters.html", results=results)

@app.route("/era, method=['GET', 'POST']")
def era():
    cursor = get_db().cursor()
    if request.method == "POST":
        book = request.form['book']
        sql =("SELECT year, description from era WHERE year LIKE %s", (book))
        data = cursor.fetchall()
        if len(data) == 0 and book == 'all': 
            sql = ("SELECT year, description from era")
            cursor.execute(sql)
            results = cursor.fetchall()
        return render_template('era.html', results=results)
    return render_template('era.html')

if __name__ == "__main__":
    app.run(debug=True)