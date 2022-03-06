from db import db
import users


def sql_edit_section(section_id, name):
    sql = "UPDATE sections SET name=:name WHERE id=:section_id"
    db.session.execute(sql, {"name": name, "section_id": section_id})
    db.session.commit()


def sql_delete_section(section_id):
    sql = "DELETE FROM sections WHERE id=:section_id"
    db.session.execute(sql, {"section_id": section_id})
    db.session.commit()


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
          " IN (SELECT SA.user_id FROM sections_access SA WHERE SA.section_id=S.id) " \
          "ORDER BY S.id DESC"
    result = db.session.execute(sql, {"user_role": user_role, "user_id": user_id})

    return result.fetchall()
