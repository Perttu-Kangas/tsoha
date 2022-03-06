from app import app
from flask import render_template, request, redirect
import users
import users_sql
import sections_sql


@app.route("/")
def index():
    return render_template("index.html", sections=sections_sql.sql_get_sections())


@app.route("/new_section", methods=["post"])
def new_section():
    users.require_admin()
    users.check_csrf()

    section_name = request.form["section_name"]

    if len(section_name) < 4 or len(section_name) > 100:
        return render_template("error.html", message="Alueen nimen tulee olla 4-100 merkkiä")

    hidden_section = 1 if request.form.get("hidden_section") else 0

    sections_sql.sql_new_section(section_name, hidden_section)

    return redirect("/")


@app.route("/add_user_to_section", methods=["post"])
def add_user_to_section():
    users.require_admin()
    users.check_csrf()

    section_id = request.form["section_id"]
    username = request.form["username"]

    if len(username) < 4 or len(username) > 20:
        return render_template("error.html", message="Tunnuksessa tulee olla 4-20 merkkiä")

    user_id = users_sql.sql_get_id_by_name(username)
    if user_id == -1:
        return render_template("error.html", message="Käyttäjää " + str(username) + " ei löytynyt")

    sections_sql.sql_add_user_to_section(section_id, user_id)

    return redirect("/")


@app.route("/delete_section", methods=["post"])
def delete_section():
    users.require_admin()
    users.check_csrf()

    section_id = request.form["section_id"]
    sections_sql.sql_delete_section(section_id)

    return redirect("/")


@app.route("/edit_section", methods=["post"])
def edit_section():
    users.require_admin()
    users.check_csrf()

    section_id = request.form["section_id"]
    section_name = request.form["section_name"]

    if len(section_name) < 4 or len(section_name) > 100:
        return render_template("error.html", message="Alueen nimen tulee olla 4-100 merkkiä")

    sections_sql.sql_edit_section(section_id, section_name)

    return redirect("/")
