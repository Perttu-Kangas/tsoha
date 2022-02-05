from db import db
import users


def new_section(name, hidden):
    sql = "INSERT INTO sections (name, hidden) " \
          "VALUES (:name, :hidden)"
    db.session.execute(sql, {"name": name, "hidden": hidden})
    db.session.commit()


def add_user_to_section(section_id, user_id):
    sql = "INSERT INTO sections_access (section_id, user_id) " \
          "VALUES (:section_id, :user_id)"
    db.session.execute(sql, {"section_id": section_id, "user_id": user_id})
    db.session.commit()


def get_sections():
    user_id = users.user_id()
    user_role = users.user_role()

    sql = "SELECT S.id, S.name, " \
          "(SELECT COUNT(T.id) FROM threads T WHERE S.id=T.section_id), S.hidden " \
          "FROM sections S " \
          "WHERE S.hidden=0 OR " + str(user_role) + "=1 OR " + str(user_id) + \
          " IN (SELECT SA.user_id FROM sections_access SA WHERE SA.section_id=S.id)"
    result = db.session.execute(sql)

    return result.fetchall()
