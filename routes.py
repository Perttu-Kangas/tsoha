from app import app
from flask import render_template, request, redirect
import users
import sections
import threads
import messages


@app.route("/")
def index():
    return render_template("index.html", sections=sections.get_sections())


# MESSAGE ROUTES START


@app.route("/section/<int:section_id>/thread/<int:thread_id>")
def thread(section_id, thread_id):
    # todo: check permission

    return render_template("thread.html", messages=messages.get_messages(thread_id),
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
    # todo: check permission

    sender_id = users.user_id()
    messages.new_message(thread_id, sender_id, message)

    return redirect("/section/" + str(section_id) + "/thread/" + str(thread_id))


# THREAD ROUTES START


@app.route("/section/<int:section_id>")
def section(section_id):
    # todo: check permission

    return render_template("section.html", threads=threads.get_threads(section_id), section_id=section_id)


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
    # todo: check permission

    sender_id = users.user_id()
    thread_id = threads.new_thread(section_id, sender_id, thread_name)[0]
    messages.new_message(thread_id, sender_id, starting_message)

    return redirect("/section/" + str(section_id))


# SECTION ROUTES START


@app.route("/new_section", methods=["post"])
def new_section():
    users.require_role(1)
    users.check_csrf()

    section_name = request.form["section_name"]

    if len(section_name) < 4 or len(section_name) > 100:
        return render_template("error.html", message="Alueen nimen tulee olla 4-100 merkkiä")

    hidden_section = 1 if request.form.get("hidden_section") else 0

    sections.new_section(section_name, hidden_section)

    return redirect("/")


@app.route("/add_user_to_section", methods=["post"])
def add_user_to_section():
    users.require_role(1)

    section_id = request.form["section_id"]
    username = request.form["username"]

    if len(username) < 4 or len(username) > 20:
        return render_template("error.html", message="Tunnuksessa tulee olla 4-20 merkkiä")

    user_id = users.get_id_by_name(username)
    if user_id == -1:
        return render_template("error.html", message="Käyttäjää " + str(username) + " ei löytynyt")

    sections.add_user_to_section(section_id, user_id)

    return redirect("/")


# USER ROUTES START


@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")


@app.route("/login", methods=["post"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if len(username) < 4 or len(username) > 20:
        return render_template("error.html", message="Tunnuksessa tulee olla 4-20 merkkiä")

    if len(password) > 40 or len(password) < 8:
        return render_template("error.html", message="Salasanan tulee olla 8-40 merkkiä")

    if not users.login(username, password):
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

    if not users.register(username, password1, role):
        return render_template("error.html", message="Rekisteröinti ei onnistunut")
    return redirect("/")
