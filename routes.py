from app import app
from flask import render_template, request, redirect
import users


@app.route("/")
def index():
    sections = "list todo"
    # 0 = id, 1 = name, 2 = threads, 3 = messages, 4 = last message
    return render_template("index.html", sections=sections)


@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")


@app.route("/login", methods=["post"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if len(username) < 4 or len(username) > 20:
        return render_template("error.html", message="Tunnuksessa tulee olla 4-20 merkkiä")

    if len(password) > 40 or len(password) < 8:
        return render_template("error.html", message="Salasanan tulee olla 8-40 merkkiä")

    if not users.login(username, password):
        return render_template("error.html", message="Väärä tunnus tai salasana")
    return redirect("/")


@app.route("/register", methods=["post"])
def register():
    username = request.form["username"]
    if len(username) < 4 or len(username) > 20:
        return render_template("error.html", message="Tunnuksessa tulee olla 4-20 merkkiä")

    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return render_template("error.html", message="Salasanat eroavat")
    if password1 == "":
        return render_template("error.html", message="Salasana on tyhjä")
    if len(password1) > 40 or len(password1) < 8:
        return render_template("error.html", message="Salasanan tulee olla 8-40 merkkiä")

    role = request.form.get("role")
    if role:
        # Admin
        role = 1
    else:
        # User
        role = 0

    if not users.register(username, password1, role):
        return render_template("error.html", message="Rekisteröinti ei onnistunut")
    return redirect("/")
