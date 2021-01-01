from flask import Flask, render_template, request, redirect, flash, url_for, session, make_response, jsonify
from flask_mysqldb import MySQL
from user import User
import json
import requests
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = "asdf16hik124"

# Configure db
db = json.load(open("db.json"))
app.config["MYSQL_HOST"] = db["mysql_host"]
app.config["MYSQL_USER"] = db["mysql_user"]
app.config["MYSQL_PASSWORD"] = db["mysql_password"]
app.config["MYSQL_DB"] = db["mysql_db"]
mysql = MySQL(app)


@app.route("/", methods=["POST", "GET"])
@app.route("/home", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        
        if request.form.get("load_next", False) == "Load Next":
            session["start_index"] += 15
            url_parameters = {
            #"key" : "AIzaSyBuc-RoTyhaqKP0LWUrJ0OTiX-G0O_aodc",
            "q" : session["q"],
            "maxResults" : 15, # change to 30
            "startIndex" : session["start_index"]
            }
        elif request.form.get("load_prev", False) == "Load Prev":
            session["start_index"] -= 15
            url_parameters = {
            #"key" : "AIzaSyBuc-RoTyhaqKP0LWUrJ0OTiX-G0O_aodc",
            "q" : session["q"],
            "maxResults" : 15, # change to 30
            "startIndex" : session["start_index"]
            }
        else:
            search = request.form["search"]
            session["q"] = search
            session["start_index"] = 0
            url_parameters = {
                #"key" : "AIzaSyBuc-RoTyhaqKP0LWUrJ0OTiX-G0O_aodc",
                "q" : search,
                "maxResults" : 15, # change to 30
                "startIndex" : session["start_index"]
            }
            
        response = requests.get("https://www.googleapis.com/books/v1/volumes", params=url_parameters)
        print(response.url)
        response_dict = response.json()

        no_more = False
        for i in range(15):
            try:
                item = response_dict['items'][i]
                try:
                    item['volumeInfo']['imageLinks']['thumbnail']
                except:
                    item['volumeInfo']['imageLinks'] = None
            except:
                # flash("No more books", category="warning")
                # passed = False
                no_more = True
                session["start_index"] = i
                break
           
        return render_template("home.html", response_dict=response_dict, search=session["q"], no_more=no_more)
    else:
        return render_template("home.html", response_dict=None, search=None)

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


@app.route("/<id>")
def book(id):
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes/{id}")
    print(response.url)
    response_dict = response.json()
    title = response_dict["volumeInfo"]["title"]

    return render_template("book.html", title=title)

if __name__ == "__main__":
    app.run(debug=True)