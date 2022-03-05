from app import app
from flask import render_template, request, redirect
from db import db
import users


# ROUTING START


@app.route("/section/<int:section_id>/thread/<int:thread_id>")
def thread(section_id, thread_id):
    if not users.sql_has_view_permission(section_id):
        return render_template("error.html", message="Sivustoa ei löytynyt")

    messages = sql_get_messages(thread_id)
    return render_template("thread.html", messages=messages,
                           section_id=section_id, thread_id=thread_id, thread_name=messages[0][5])


@app.route("/new_message", methods=["post"])
def new_message():
    if not users.is_logged_in():
        return render_template("error.html", message="Täytyy olla kirjautunut sisään lähettääkseen viestin")

    users.check_csrf()

    message = request.form["message"]

    if len(message) < 1 or len(message) > 2000:
        return render_template("error.html", message="Viestin tulee olla 1-2000 merkkiä")

    section_id = request.form["section_id"]
    thread_id = request.form["thread_id"]

    if not users.sql_has_view_permission(section_id):
        return render_template("error.html", message="Sivustoa ei löytynyt")

    sender_id = users.user_id()
    sql_new_message(thread_id, sender_id, message)

    return redirect("/section/" + str(section_id) + "/thread/" + str(thread_id))


@app.route("/delete_message", methods=["post"])
def delete_message():
    if not users.is_logged_in():
        return render_template("error.html", message="Täytyy olla kirjautunut sisään poistaakseen viestin")

    users.check_csrf()

    message_id = request.form["message_id"]

    if not users.sql_has_message_edit_permission(message_id):
        return render_template("error.html", message="Sivustoa ei löytynyt")

    thread_id = sql_delete_message(message_id)[0]
    section_id = sql_get_section_id(thread_id)[0]

    return redirect("/section/" + str(section_id) + "/thread/" + str(thread_id))


@app.route("/edit_message", methods=["post"])
def edit_message():
    if not users.is_logged_in():
        return render_template("error.html", message="Täytyy olla kirjautunut sisään muokatakseen ketjua")

    users.check_csrf()

    message = request.form["message"]

    if len(message) < 1 or len(message) > 2000:
        return render_template("error.html", message="Viestin tulee olla 1-2000 merkkiä")

    message_id = request.form["message_id"]

    if not users.sql_has_message_edit_permission(message_id):
        return render_template("error.html", message="Sivustoa ei löytynyt")

    sql_edit_message(message_id, message)
    section_id = request.form["section_id"]
    thread_id = request.form["thread_id"]

    return redirect("/section/" + str(section_id) + "/thread/" + str(thread_id))


@app.route("/find_message")
def find_message():
    message = request.form["message"]
    if len(message) < 3 or len(message) > 20:
        return render_template("error.html", message="Viestin etsinnän tulee olla 3-20 merkkiä")

    messages = sql_find_messages(message)
    if messages is None:
        return render_template("error.html", message="Hakusanalla " + message + " ei löytynt viestejä.")

    return render_template("find.html", messages=messages)


# ROUTING END


def sql_edit_message(message_id, message):
    sql = "UPDATE messages SET message=:message WHERE id=:message_id"
    db.session.execute(sql, {"message": message, "message_id": message_id})
    db.session.commit()


def sql_get_section_id(thread_id):
    sql = "SELECT section_id FROM threads WHERE id=:thread_id"
    result = db.session.execute(sql, {"thread_id": thread_id})
    return result.fetchone()


def sql_get_thread_name(thread_id):
    sql = "SELECT name FROM threads WHERE id=:thread_id"
    result = db.session.execute(sql, {"thread_id": thread_id})
    return result.fetchone()


def sql_delete_message(message_id):
    sql = "DELETE FROM messages WHERE id=:message_id RETURNING thread_id"
    result = db.session.execute(sql, {"message_id": message_id})
    db.session.commit()
    return result.fetchone()


def sql_new_message(thread_id, sender_id, message):
    sql = "INSERT INTO messages (thread_id, sender_id, sent_at, message) " \
          "VALUES (:thread_id, :sender_id, NOW(), :message)"
    db.session.execute(sql, {"thread_id": thread_id, "sender_id": sender_id, "message": message})
    db.session.commit()


def sql_get_messages(thread_id):
    user_id = users.user_id()
    user_role = users.user_role()
    sql = "SELECT U.username, M.sent_at, M.message, M.id, (M.sender_id=:user_id OR :user_role>0), T.name " \
          "FROM users U, messages M, threads T WHERE M.thread_id=:thread_id AND U.id=M.sender_id AND T.id=:thread_id " \
          "ORDER BY M.id"

    result = db.session.execute(sql, {"thread_id": thread_id, "user_id": user_id, "user_role": user_role})
    return result.fetchall()


def sql_find_messages(message):
    user_id = users.user_id()
    user_role = users.user_role()

    sql = "SELECT S.id, S.name, T.id, T.name, M.id, M.message, M.sent_at " \
          "FROM sections S, sections_access SA, threads T, messages M " \
          "WHERE M.message LIKE :message AND M.thread_id=T.id AND T.section_id=S.id " \
          "AND (S.hidden=0 OR :user_role=1 OR :user_id" \
          " IN (SELECT SA.user_id FROM sections_access SA WHERE SA.section_id=S.id))" \
          "ORDER BY M.sent_at"

    result = db.session.execute(sql, {"message": "%" + message + "%", "user_id": user_id, "user_role": user_role})
    return result.fetchall()
