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
        # Most likely same username already exists...
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


def get_id_by_name(username):
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
    return -1 if not user else user[0]


def logout():
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


def has_view_permission(section_id):
    if user_role() > 0:
        # Admin
        return True

    sql = "SELECT S.id FROM sections S " \
          "WHERE S.id=:section_id AND (S.hidden=0 OR :user_id IN " \
          "(SELECT SA.user_id FROM sections_access SA WHERE SA.section_id=S.id))"
    result = db.session.execute(sql, {"section_id": section_id, "user_id": user_id()})
    return not result.fetchone()


def has_section_edit_permission():
    return user_role() > 0


def has_thread_edit_permission(thread_id):
    if user_role() > 0:
        # Admin
        return True

    sql = "SELECT id FROM threads WHERE id=:thread_id AND creator_id=:user_id"
    result = db.session.execute(sql, {"thread_id": thread_id, "user_id": user_id()})
    return not result.fetchone()


def has_message_edit_permission(message_id):
    if user_role() > 0:
        # Admin
        return True

    sql = "SELECT id FROM messages WHERE id=:message_id AND sender_id=:user_id"
    result = db.session.execute(sql, {"message_id": message_id, "user_id": user_id()})
    return not result.fetchone()


def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
