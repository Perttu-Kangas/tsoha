import os
from db import db
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
import users


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


def sql_has_thread_edit_permission(thread_id):
    if users.user_role() == 1:
        # Admin
        return True

    sql = "SELECT id FROM threads WHERE id=:thread_id AND creator_id=:user_id"
    result = db.session.execute(sql, {"thread_id": thread_id, "user_id": users.user_id()})
    return result.fetchone() is not None


def sql_has_message_edit_permission(message_id):
    if users.user_role() == 1:
        # Admin
        return True

    sql = "SELECT id FROM messages WHERE id=:message_id AND sender_id=:user_id"
    result = db.session.execute(sql, {"message_id": message_id, "user_id": users.user_id()})
    return result.fetchone() is not None


def sql_has_view_permission(section_id):
    if users.user_role() == 1:
        # Admin
        return True

    sql = "SELECT S.id FROM sections S " \
          "WHERE S.id=:section_id AND (S.hidden=0 OR :user_id IN " \
          "(SELECT SA.user_id FROM sections_access SA WHERE SA.section_id=S.id))"
    result = db.session.execute(sql, {"section_id": section_id, "user_id": users.user_id()})
    return result.fetchone() is not None
