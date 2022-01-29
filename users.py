import os
from db import db
from flask import abort, request, session
from werkzeug.security import check_password_hash, generate_password_hash


def register(username, password, role):
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
        return False
    return login(username, password)


def login(name, password):
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


def logout():
    del session["user_id"]
    del session["user_role"]


def user_id():
    return session.get("user_id", 0)


def get_user_role():
    return session.get("user_role", 0)


def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
