from flask_mysqldb import MySQL
from flask import flash

class User:
    def __init__(self, first_name="", last_name="", email="", password="", user_id=None):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password

    def check_passed(self):
        check = True

        # if email_duplicate == 1:
        #     check = False
        #     return "Email already exsists"
        if len(self.email) > 320: 
            check = False
            return "Email excedes the maximiun number of characters"
        if len(self.first_name) > 45:
            check = False
            return "First name excedes the maximiun number of characters"
        if len(self.last_name) > 45:
            check = False
            return "First name excedes the maximiun number of characters"
        # if new_password != None and confirm_new_password != None:
        #     if new_password == confirm_new_password:
        #         self.password = new_password
        #     else:
        #         return flash("New passwords do not match")
        # TODO: password hashing and add extra strength 

        return check

    def register(self, mysql):
        cur = mysql.connection.cursor()
        email_duplicate = cur.execute("SELECT * FROM users WHERE email=%s", (self.email,))
        
        if email_duplicate != 0:
            return "Email already exists"

        if self.check_passed() == True:
            try:
                cur.execute("INSERT INTO users(firstName, lastName, email, password) VALUES(%s, %s, %s, %s)", 
                            (self.first_name, self.last_name, self.email, self.password))
                cur.execute("SELECT LAST_INSERT_ID();")
                self.user_id = cur.fetchall()[0][0]
                cur.connection.commit()
                cur.close()
                return True
            except mysql.connection.IntegrityError as err:
                return "Invalid input"
        else:
            return "Failed"

    def update(self, mysql, first_name, last_name, email, password, new_password, confirm_new_password):
        if new_password == "" or confirm_new_password == "":
            # user does not want to change password
            if self.password == password:
                self.first_name = first_name
                self.last_name = last_name
                self.email = email

                cur = mysql.connection.cursor()
                if self.check_passed():
                    cur.execute(f"UPDATE users SET firstName=%s, lastName=%s, email=%s WHERE userId={self.user_id};", 
                            (self.first_name, self.last_name, self.email))
                    cur.connection.commit()
                    return True
                else:
                    return False
            else:
                return flash("Password is incorrect", "danger")
        else:
            return flash("New passwords do not match", "danger")

        # if self.check_passed(new_password, confirm_new_password):
        #     cur = mysql.connection.cursor()
        #     try:
        #         cur.execute(f"UPDATE users SET firstName=%s, lastName=%s, email=%s, password=%s WHERE name LIKE {self.user_id};", 
        #                     (self.first_name, self.last_name, self.email, self.password))
        #     except:
        #         return False
                
        #     cur.connection.commit()
        #     cur.close()
        #     return True
        # else:
        #     return "Update info faled"

    @staticmethod
    def login(mysql, email, password):
        cur = mysql.connection.cursor()
        user = cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        if user == 1:
            # TODO: create a user class
            user_details = cur.fetchall()
            return User(user_details[0][1], user_details[0][2], user_details[0][3], user_details[0][4], user_details[0][0], )
        else:
            return None

    @staticmethod
    def users(mysql):
        cur = mysql.connection.cursor()
        users_row_count = cur.execute("SELECT * FROM users")
        if users_row_count > 0:
            users_row = cur.fetchall()
            return users_row
        else:
            return None

    @staticmethod
    def jsonToObj(jsonDict):
        user_id = jsonDict["user_id"]
        first_name = jsonDict["first_name"]
        last_name = jsonDict["last_name"]
        email = jsonDict["email"]
        password = jsonDict["password"]

        return User(first_name, last_name, email, password, user_id)
