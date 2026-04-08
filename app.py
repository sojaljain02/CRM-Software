from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret"

DB = "database.db"


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY, name TEXT, status TEXT)")

    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        result = c.fetchone()
        conn.close()

        if result:
            session["user"] = user
            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM customers")
    customers = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM leads")
    leads = c.fetchone()[0]

    conn.close()

    return render_template("dashboard.html", customers=customers, leads=leads)


@app.route("/customers", methods=["GET", "POST"])
def customers():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        c.execute("INSERT INTO customers (name, email) VALUES (?, ?)", (name, email))
        conn.commit()

    c.execute("SELECT * FROM customers")
    data = c.fetchall()

    conn.close()
    return render_template("customers.html", data=data)


@app.route("/leads", methods=["GET", "POST"])
def leads():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        status = request.form["status"]
        c.execute("INSERT INTO leads (name, status) VALUES (?, ?)", (name, status))
        conn.commit()

    c.execute("SELECT * FROM leads")
    data = c.fetchall()

    conn.close()
    return render_template("leads.html", data=data)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    init_db()

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin')")
    conn.commit()
    conn.close()

    app.run(debug=True)