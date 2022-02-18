from app import app
from flask import render_template, request, redirect
from db import db
import users


@app.route("/section/<int:section_id>/thread/<int:thread_id>")
def thread(section_id, thread_id):
    if not users.sql_has_view_permission(section_id):
        return render_template("error.html", message="Sivustoa ei löytynyt")

    return render_template("thread.html", messages=sql_get_messages(thread_id),
                           section_id=section_id, thread_id=thread_id)


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


def sql_new_message(thread_id, sender_id, message):
    sql = "INSERT INTO messages (thread_id, sender_id, sent_at, message) " \
          "VALUES (:thread_id, :sender_id, NOW(), :message)"
    db.session.execute(sql, {"thread_id": thread_id, "sender_id": sender_id, "message": message})
    db.session.commit()


def sql_get_messages(thread_id):
    sql = "SELECT U.username, M.sent_at, M.message " \
          "FROM users U, messages M WHERE M.thread_id=:thread_id AND U.id=M.sender_id " \
          "ORDER BY M.id"

    result = db.session.execute(sql, {"thread_id": thread_id})
    return result.fetchall()
