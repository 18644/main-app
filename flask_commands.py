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

@app.route("/searchE", methods=['GET', 'POST'])
def era():
    cursor = get_db().cursor()
    if request.method == "POST":
        era = request.values['era']
        sql =("SELECT year, description from era WHERE year LIKE %s", (era))
        results = cursor.fetchall()
        if len(results) == 0 and era == 'all': 
            sql = ("SELECT year, description from era")
            cursor.execute(sql)
            results = cursor.fetchall()
        return render_template('searchE.html', results=results)
    return render_template('searchE.html')

@app.route('/insertE', methods=['GET', 'POST'])
def insert():
    cursor = get_db().cursor()
    if request.method == "POST":
        era = request.values['era']
        sql = ("INSERT INTO era (year, description) Values (%s)", (era))
        cursor.execute(sql)
        return redirect("http://localhost:5000/searchE", code=302)
    return render_template('insertE.html')

if __name__ == "__main__":
    app.run(debug=True)