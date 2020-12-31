from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_mysqldb import MySQL
from user import User
import json
app = Flask(__name__)
app.config["SECRET_KEY"] = "asdf16hik124"

# Configure db
db = json.load(open("db.json"))
app.config["MYSQL_HOST"] = db["mysql_host"]
app.config["MYSQL_USER"] = db["mysql_user"]
app.config["MYSQL_PASSWORD"] = db["mysql_password"]
app.config["MYSQL_DB"] = db["mysql_db"]
mysql = MySQL(app)


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

        member = User(first_name, last_name, email, password)
        if member.register(mysql) == True:
            flash("Registered successfully!", category="success")
            session["user"] = json.dumps(member.__dict__)
            session["logged_in"] = True
            return redirect("/users")
    else:
        return render_template("register.html")

@app.route("/login",  methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        checkbox = request.form.get("checkbox", False)
        member = User.login(mysql, email, password)

        if member != None:
            session["user"] = json.dumps(member.__dict__)
            session["logged_in"] = True

            if checkbox == "on":
                session["remember_me"] = True
                session["email"] = member.email
                session["password"] = member.password
            else:
                if "email" in session or "password" in session:
                    session.pop("email", None)
                    session.pop("password", None)
                    session["remember_me"] = False

            flash(f"Logged in as \"{member.email}\"", category="success")
            return redirect("/home")
        else:
            flash("No user found!", category="danger")
            return render_template("login.html")
    else:
        return render_template("login.html")

#TODO: authenticate information 
@app.route("/users")
def users():
    if "logged_in" not in session:
        flash("Please login to view users", "warning")
        return redirect("/login")
    else:
        users_row = User.users(mysql)
        if users_row != None:
            return render_template("users.html", users_row=users_row)
        else:
            return "No Users"

@app.route("/profile", methods=["POST", "GET"])
def profile():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]
        new_password = request.form["new_password"]
        confirm_new_password = request.form["confirm_new_password"]

        #member = User(first_name, last_name, email, password)
        member = User.jsonToObj(json.loads(session["user"]))
        update = member.update(mysql, first_name, last_name, email, password, new_password, confirm_new_password)
        
        # if member.password == password:
        #     pass
        # else:
        #     flash("Password is incorrect", "danger")


        if update == True:
            flash("Updated account successfully!", category="suxxess")
            session["user"] = json.dumps(member.__dict__)
            print(session)
            return redirect("/users")
        else:
            return redirect("/profile")
    else:
        return render_template("profile.html", user=json.loads(session["user"]))

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("logged_in", None)
    flash("Logged out!", "success")
    return redirect("/home")

    cur.close()
if __name__ == "__main__":
    app.run(debug=True)