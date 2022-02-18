from app import app
from flask import render_template, request, redirect
from db import db
import users

# ROUTING START


@app.route("/")
def index():
    return render_template("index.html", sections=sql_get_sections())


@app.route("/new_section", methods=["post"])
def new_section():
    users.require_role(1)
    users.check_csrf()

    section_name = request.form["section_name"]

    if len(section_name) < 4 or len(section_name) > 100:
        return render_template("error.html", message="Alueen nimen tulee olla 4-100 merkkiä")

    hidden_section = 1 if request.form.get("hidden_section") else 0

    sql_new_section(section_name, hidden_section)

    return redirect("/")


@app.route("/add_user_to_section", methods=["post"])
def add_user_to_section():
    users.require_role(1)

    section_id = request.form["section_id"]
    username = request.form["username"]

    if len(username) < 4 or len(username) > 20:
        return render_template("error.html", message="Tunnuksessa tulee olla 4-20 merkkiä")

    user_id = users.sql_get_id_by_name(username)
    if user_id == -1:
        return render_template("error.html", message="Käyttäjää " + str(username) + " ei löytynyt")

    sql_add_user_to_section(section_id, user_id)

    return redirect("/")


# ROUTING END


def sql_new_section(name, hidden):
    sql = "INSERT INTO sections (name, hidden) " \
          "VALUES (:name, :hidden)"
    db.session.execute(sql, {"name": name, "hidden": hidden})
    db.session.commit()


def sql_add_user_to_section(section_id, user_id):
    sql = "INSERT INTO sections_access (section_id, user_id) " \
          "VALUES (:section_id, :user_id)"
    db.session.execute(sql, {"section_id": section_id, "user_id": user_id})
    db.session.commit()


def sql_get_sections():
    user_id = users.user_id()
    user_role = users.user_role()

    sql = "SELECT S.id, S.name, " \
          "(SELECT COUNT(T.id) FROM threads T WHERE S.id=T.section_id), S.hidden " \
          "FROM sections S " \
          "WHERE S.hidden=0 OR :user_role=1 OR :user_id" + \
          " IN (SELECT SA.user_id FROM sections_access SA WHERE SA.section_id=S.id)"
    result = db.session.execute(sql, {"user_role": user_role, "user_id": user_id})

    return result.fetchall()
