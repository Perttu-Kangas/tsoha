from app import app
from flask import render_template, request, redirect
import users
import users_sql
import messages_sql
import threads_sql


@app.route("/section/<int:section_id>")
def section(section_id):
    if not users_sql.sql_has_view_permission(section_id):
        return render_template("error.html", message="Sivustoa ei löytynyt")

    return render_template("section.html", threads=threads_sql.sql_get_threads(section_id), section_id=section_id,
                           section_name=threads_sql.sql_get_section_name(section_id))


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

    if not users_sql.sql_has_view_permission(section_id):
        return render_template("error.html", message="Sivustoa ei löytynyt")

    sender_id = users.user_id()
    thread_id = threads_sql.sql_new_thread(section_id, sender_id, thread_name)[0]
    messages_sql.sql_new_message(thread_id, sender_id, starting_message)

    return redirect("/section/" + str(section_id))


@app.route("/delete_thread", methods=["post"])
def delete_thread():
    if not users.is_logged_in():
        return render_template("error.html", message="Täytyy olla kirjautunut sisään poistaakseen ketjun")

    users.check_csrf()

    thread_id = request.form["thread_id"]

    if not users_sql.sql_has_thread_edit_permission(thread_id):
        return render_template("error.html", message="Sivustoa ei löytynyt")

    section_id = threads_sql.sql_delete_thread(thread_id)[0]

    return redirect("/section/" + str(section_id))


@app.route("/edit_thread", methods=["post"])
def edit_thread():
    if not users.is_logged_in():
        return render_template("error.html", message="Täytyy olla kirjautunut sisään muokatakseen ketjua")

    users.check_csrf()

    thread_name = request.form["thread_name"]

    if len(thread_name) < 4 or len(thread_name) > 100:
        return render_template("error.html", message="Alueen nimen tulee olla 4-100 merkkiä")

    thread_id = request.form["thread_id"]

    if not users_sql.sql_has_thread_edit_permission(thread_id):
        return render_template("error.html", message="Sivustoa ei löytynyt")

    threads_sql.sql_edit_thread(thread_id, thread_name)
    section_id = request.form["section_id"]

    return redirect("/section/" + str(section_id))
