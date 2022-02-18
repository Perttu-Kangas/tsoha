from app import app
from flask import render_template, request, redirect
from db import db
import users
import messages

# ROUTING START


@app.route("/section/<int:section_id>")
def section(section_id):
    if not users.sql_has_view_permission(section_id):
        return render_template("error.html", message="Sivustoa ei löytynyt")

    return render_template("section.html", threads=sql_get_threads(section_id), section_id=section_id)


@app.route("/new_thread", methods=["post"])
def new_thread():

    if not users.is_logged_in():
        return render_template("error.html", message="Täytyy olla kirjautunut sisään luodakseen ketjun")

    users.check_csrf()

    thread_name = request.form["thread_name"]

    if len(thread_name) < 4 or len(thread_name) > 100:
        return render_template("error.html", message="Ketjun nimen tulee olla 4-100 merkkiä")

    starting_message = request.form["message"]

    if len(starting_message) < 1 or len(starting_message) > 2000:
        return render_template("error.html", message="Viestin tulee olla 1-2000 merkkiä")

    section_id = request.form["section_id"]

    if not users.sql_has_view_permission(section_id):
        return render_template("error.html", message="Sivustoa ei löytynyt")

    sender_id = users.user_id()
    thread_id = sql_new_thread(section_id, sender_id, thread_name)[0]
    messages.sql_new_message(thread_id, sender_id, starting_message)

    return redirect("/section/" + str(section_id))


# ROUTING END


def sql_new_thread(section_id, creator_id, name):
    sql = "INSERT INTO threads (section_id, creator_id, name) " \
          "VALUES (:section_id, :creator_id, :name) RETURNING id"
    result = db.session.execute(sql, {"section_id": section_id, "creator_id": creator_id, "name": name})
    db.session.commit()
    return result.fetchone()


def sql_get_threads(section_id):
    sql = "SELECT T.id, T.name, " \
          "(SELECT COUNT(M.id) FROM messages M WHERE T.id=M.thread_id), U.username " \
          "FROM users U, threads T WHERE T.section_id=:section_id AND U.id=T.creator_id"

    result = db.session.execute(sql, {"section_id": section_id})
    return result.fetchall()
