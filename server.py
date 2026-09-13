
from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

app.secret_key = "employee_management_secret_key"


# ==================================================
# USER DATABASE
# ==================================================

def create_user_database():

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# ==================================================
# EMPLOYEE DATABASE
# ==================================================

def create_employee_database():

    connection = sqlite3.connect("employees.db")
    cursor = connection.cursor()

    # Create employees table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            department TEXT NOT NULL
        )
    """)

    # Check which columns already exist
    cursor.execute("PRAGMA table_info(employees)")
    columns = cursor.fetchall()

    column_names = [column[1] for column in columns]

    # Add salary if it is missing
    if "salary" not in column_names:
        cursor.execute("""
            ALTER TABLE employees
            ADD COLUMN salary TEXT DEFAULT '0'
        """)

    connection.commit()
    connection.close()


# Create databases
create_user_database()
create_employee_database()


# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():

    return render_template("home.html")


# ==================================================
# REGISTER
# ==================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    message = ""

    if request.method == "POST":

        fullname = request.form["fullname"]
        username = request.form["username"]
        password = request.form["password"]

        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()

        try:

            cursor.execute("""
                INSERT INTO users
                (fullname, username, password)
                VALUES (?, ?, ?)
            """, (fullname, username, password))

            connection.commit()
            connection.close()

            return redirect("/login")

        except sqlite3.IntegrityError:

            connection.close()

            message = "Username already exists!"

    return render_template(
        "register.html",
        message=message
    )


# ==================================================
# LOGIN
# ==================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    message = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM users
            WHERE username = ? AND password = ?
        """, (username, password))

        user = cursor.fetchone()

        connection.close()

        if user:

            session["username"] = username
            session["fullname"] = user[1]

            return redirect("/")

        else:

            message = "Incorrect username or password!"

    return render_template(
        "login.html",
        message=message
    )


# ==================================================
# EMPLOYEE
# ==================================================

@app.route("/employee")
def employee():

    connection = sqlite3.connect("employees.db")

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM employees
        ORDER BY id DESC
    """)

    employees = cursor.fetchall()

    connection.close()

    return render_template(
        "employee.html",
        employees=employees
    )


# ==================================================
# ADD EMPLOYEE
# ==================================================

@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        salary = request.form["salary"]

        connection = sqlite3.connect("employees.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO employees
            (name, email, phone, department, salary)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            email,
            phone,
            department,
            salary
        ))

        connection.commit()
        connection.close()

        return redirect("/employee")

    return render_template("add_employee.html")


# ==================================================
# SEARCH EMPLOYEE
# ==================================================

@app.route("/search", methods=["GET", "POST"])
def search():

    employees = []

    if request.method == "POST":

        search_name = request.form["search"]

        connection = sqlite3.connect("employees.db")

        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM employees
            WHERE name LIKE ?
        """, ("%" + search_name + "%",))

        employees = cursor.fetchall()

        connection.close()

    return render_template(
        "search.html",
        employees=employees
    )


# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ==================================================
# START APPLICATION
# ==================================================

if __name__ == "__main__":

    app.run(debug=True)