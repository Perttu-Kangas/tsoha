from app import app
from flask import render_template, request, redirect
import users
import users_sql
import messages_sql


@app.route("/section/<int:section_id>/thread/<int:thread_id>")
def thread(section_id, thread_id):
    if not users_sql.sql_has_view_permission(section_id):
        return render_template("error.html", message="Sivustoa ei löytynyt")

    return render_template("thread.html", messages=messages_sql.sql_get_messages(thread_id),
                           section_id=section_id, thread_id=thread_id,
                           path=messages_sql.sql_get_path(section_id, thread_id))


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

    if not users_sql.sql_has_view_permission(section_id):
        return render_template("error.html", message="Sivustoa ei löytynyt")

    sender_id = users.user_id()
    messages_sql.sql_new_message(thread_id, sender_id, message)

    return redirect("/section/" + str(section_id) + "/thread/" + str(thread_id))


@app.route("/delete_message", methods=["post"])
def delete_message():
    if not users.is_logged_in():
        return render_template("error.html", message="Täytyy olla kirjautunut sisään poistaakseen viestin")

    users.check_csrf()

    message_id = request.form["message_id"]

    if not users_sql.sql_has_message_edit_permission(message_id):
        return render_template("error.html", message="Sivustoa ei löytynyt")

    thread_id = messages_sql.sql_delete_message(message_id)[0]
    section_id = messages_sql.sql_get_section_id(thread_id)[0]

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

    if not users_sql.sql_has_message_edit_permission(message_id):
        return render_template("error.html", message="Sivustoa ei löytynyt")

    messages_sql.sql_edit_message(message_id, message)
    section_id = request.form["section_id"]
    thread_id = request.form["thread_id"]

    return redirect("/section/" + str(section_id) + "/thread/" + str(thread_id))


@app.route("/find_message")
def find_message():
    message = request.args["message"]
    if len(message) < 3 or len(message) > 20:
        return render_template("error.html", message="Viestin etsinnän tulee olla 3-20 merkkiä")

    messages = messages_sql.sql_find_messages(message)
    if messages is None or len(messages) == 0:
        return render_template("error.html", message="Hakusanalla " + message + " ei löytynt viestejä.")

    return render_template("find.html", messages=messages)


@app.route("/like_message", methods=["post"])
def like_message():
    if not users.is_logged_in():
        return render_template("error.html", message="Täytyy olla kirjautunut sisään poistaakseen viestin")

    users.check_csrf()

    section_id = request.form["section_id"]
    thread_id = request.form["thread_id"]
    message_id = request.form["message_id"]

    if not users_sql.sql_has_view_permission(section_id):
        return render_template("error.html", message="Sivustoa ei löytynyt")

    if not messages_sql.sql_has_liked_message(message_id):
        messages_sql.sql_like_message(message_id)

    return redirect("/section/" + str(section_id) + "/thread/" + str(thread_id) + "#" + str(message_id))
