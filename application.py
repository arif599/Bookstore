from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
import json
app = Flask(__name__)

# Configure db
db = json.load(open("db.json"))
app.config["MYSQL_HOST"] = db["mysql_host"]
app.config["MYSQL_USER"] = db["mysql_user"]
app.config["MYSQL_PASSWORD"] = db["mysql_password"]
app.config["MYSQL_DB"] = db["mysql_db"]
mysql = MySQL(app)

# TODO: add search bar
@app.route("/")
@app.route("/home")
def home():        
    return render_template("home.html")

@app.route("/register", methods=["POST", "GET"])
def register(): 
    if request.method == "POST":
        # Store information sent from the form in DB
        # Fetch form data
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(firstName, lastName, email, password) VALUES(%s, %s, %s, %s)", 
                    (first_name, last_name, email, password))
        cur.connection.commit()
        cur.close()
        return redirect("/users")
    else:
        return render_template("register.html")

# TODO: Finish Login and add sessions
@app.route("/login",  methods=["POST", "GET"])
def login():
    if request.method == "POST":
        pass
    else:
        return render_template("login.html")

#TODO: authenticate information 
@app.route("/users")
def users():
    cur = mysql.connection.cursor()
    users_row_count = cur.execute("SELECT * FROM users")
    if users_row_count > 0:
        users_row = cur.fetchall()
        return render_template("users.html", users_row=users_row)
        cur.close()
    else:
        return "No Users"
    


    cur.close()
if __name__ == "__main__":
    app.run(debug=True)