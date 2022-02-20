from app import app
import os
from db import db
from flask import abort, request, session, render_template, redirect
from werkzeug.security import check_password_hash, generate_password_hash

# ROUTING START


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

    if len(password) > 40 or len(password) < 8:
        return render_template("error.html", message="Salasanan tulee olla 8-40 merkkiä")

    if not sql_login(username, password):
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

    role = 1 if request.form.get("role") else 0

    if not sql_register(username, password1, role):
        return render_template("error.html", message="Rekisteröinti ei onnistunut")
    return redirect("/")


# ROUTING END

def sql_register(username, password, role):
    # In reality role wouldn't be made like this,
    # but since this is purely made for this course
    # and people have to be able to test with admin role

    hash_value = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username, password, role) " \
              "VALUES (:username, :password, :role)"
        db.session.execute(sql, {"username": username, "password": hash_value, "role": role})
        db.session.commit()
    except:
        # Most likely same username already exists...
        return False
    return sql_login(username, password)


def sql_login(name, password):
    sql = "SELECT id, password, role FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username": name})
    user = result.fetchone()
    if not user:
        return False
    if not check_password_hash(user[1], password):
        return False
    session["user_id"] = user[0]
    session["user_role"] = user[2]
    session["csrf_token"] = os.urandom(16).hex()
    return True


def sql_get_id_by_name(username):
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
    return -1 if not user else user[0]


def session_logout():
    del session["user_id"]
    del session["user_role"]


def user_id():
    return session.get("user_id", 0)


def is_logged_in():
    return user_id() > 0


def user_role():
    return session.get("user_role", 0)


def require_role(role):
    if role < user_role():
        abort(403)


def sql_has_view_permission(section_id):
    if user_role() > 0:
        # Admin
        return True

    sql = "SELECT S.id FROM sections S " \
          "WHERE S.id=:section_id AND (S.hidden=0 OR :user_id IN " \
          "(SELECT SA.user_id FROM sections_access SA WHERE SA.section_id=S.id))"
    result = db.session.execute(sql, {"section_id": section_id, "user_id": user_id()})
    return result.fetchone() is not None


def has_section_edit_permission():
    return user_role() > 0


def sql_has_thread_edit_permission(thread_id):
    if user_role() > 0:
        # Admin
        return True

    sql = "SELECT id FROM threads WHERE id=:thread_id AND creator_id=:user_id"
    result = db.session.execute(sql, {"thread_id": thread_id, "user_id": user_id()})
    return result.fetchone() is not None


def sql_has_message_edit_permission(message_id):
    if user_role() > 0:
        # Admin
        return True

    sql = "SELECT id FROM messages WHERE id=:message_id AND sender_id=:user_id"
    result = db.session.execute(sql, {"message_id": message_id, "user_id": user_id()})
    return result.fetchone() is not None


def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
