from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

app.secret_key = "employee_management_secret_key"

DATABASE = "users.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# CREATE DATABASE
# =========================================================

def create_database():

    conn = get_db()
    cursor = conn.cursor()

    # -----------------------------------------------------
    # USERS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # -----------------------------------------------------
    # EMPLOYEES TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            phone TEXT,
            department TEXT,
            salary TEXT,
            joining_date TEXT,
            address TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("home.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    error = ""

    if request.method == "POST":

        fullname = request.form["fullname"]
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        try:

            # Save user in users table
            cursor.execute("""
                INSERT INTO users
                (fullname, username, password)
                VALUES (?, ?, ?)
            """, (
                fullname,
                username,
                password
            ))

            # Automatically create employee record
            cursor.execute("""
                INSERT INTO employees
                (fullname, username, password)
                VALUES (?, ?, ?)
            """, (
                fullname,
                username,
                password
            ))

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            return render_template(
                "registerdemo.html",
                error="Username already exists!"
            )

        conn.close()

        return redirect("/login")

    return render_template(
        "registerdemo.html",
        error=error
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    error = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM users
            WHERE username = ?
            AND password = ?
        """, (
            username,
            password
        ))

        user = cursor.fetchone()

        conn.close()

        if user:

            # Store login information
            session["fullname"] = user["fullname"]
            session["username"] = user["username"]

            return redirect("/")

        else:

            error = "Username or password incorrect!"

    return render_template(
        "login.html",
        error=error
    )


# =========================================================
# ADD EMPLOYEE
# =========================================================

@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():

    if request.method == "POST":

        fullname = request.form["fullname"]
        username = request.form["username"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        salary = request.form["salary"]
        joining_date = request.form["joining_date"]
        address = request.form["address"]

        conn = get_db()
        cursor = conn.cursor()

        # Check whether this registered username
        # already exists in employee table
        cursor.execute("""
            SELECT *
            FROM employees
            WHERE username = ?
        """, (username,))

        existing_employee = cursor.fetchone()

        if existing_employee:

            # Update existing registered employee
            cursor.execute("""
                UPDATE employees
                SET fullname = ?,
                    email = ?,
                    phone = ?,
                    department = ?,
                    salary = ?,
                    joining_date = ?,
                    address = ?
                WHERE username = ?
            """, (
                fullname,
                email,
                phone,
                department,
                salary,
                joining_date,
                address,
                username
            ))

        else:

            # Add completely new employee
            cursor.execute("""
                INSERT INTO employees
                (
                    fullname,
                    username,
                    email,
                    phone,
                    department,
                    salary,
                    joining_date,
                    address
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fullname,
                username,
                email,
                phone,
                department,
                salary,
                joining_date,
                address
            ))

        conn.commit()
        conn.close()

        return redirect("/employee")

    return render_template("add_employee.html")


# =========================================================
# EMPLOYEE LIST
# =========================================================

@app.route("/employee")
def employee():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM employees
        ORDER BY id DESC
    """)

    employees = cursor.fetchall()

    conn.close()

    return render_template(
        "employee.html",
        employees=employees
    )


# =========================================================
# SEARCH EMPLOYEE
# =========================================================

@app.route("/search")
def search():

    keyword = request.args.get("keyword", "").strip()

    employees = []

    if keyword:

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM employees
            WHERE fullname LIKE ?
               OR username LIKE ?
               OR email LIKE ?
               OR department LIKE ?
        """, (
            "%" + keyword + "%",
            "%" + keyword + "%",
            "%" + keyword + "%",
            "%" + keyword + "%"
        ))

        employees = cursor.fetchall()

        conn.close()

    return render_template(
        "search.html",
        employees=employees,
        keyword=keyword
    )


# =========================================================
# DELETE EMPLOYEE
# =========================================================

@app.route("/delete_employee/<int:id>")
def delete_employee(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM employees
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect("/employee")


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    create_database()

    app.run(debug=True)
    