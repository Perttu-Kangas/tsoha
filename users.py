from app import app
from flask import abort, request, session, render_template, redirect
import users_sql


@app.route("/logout")
def logout():
    session_logout()
    return redirect("/")


@app.route("/login", methods=["post"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if len(username) < 4 or len(username) > 20:
        return render_template("error.html", message="Tunnuksessa tulee olla 4-20 merkkiä")

    if len(password) < 8 or len(password) > 40:
        return render_template("error.html", message="Salasanan tulee olla 8-40 merkkiä")

    if not users_sql.sql_login(username, password):
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
    if len(password1) < 8 or len(password1) > 40:
        return render_template("error.html", message="Salasanan tulee olla 8-40 merkkiä")

    role = 1 if request.form.get("role") else 0

    if not users_sql.sql_register(username, password1, role):
        return render_template("error.html", message="Rekisteröinti ei onnistunut")
    return redirect("/")


def session_logout():
    del session["user_id"]
    del session["user_role"]
    del session["csrf_token"]


def user_id():
    return session.get("user_id", 0)


def is_logged_in():
    return user_id() > 0


def user_role():
    return session.get("user_role", 0)


def require_admin():
    if user_role() == 0:
        abort(403)


def has_section_edit_permission():
    return user_role() == 1


def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
