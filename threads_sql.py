from db import db
import users


def sql_edit_thread(thread_id, name):
    sql = "UPDATE threads SET name=:name WHERE id=:thread_id"
    db.session.execute(sql, {"name": name, "thread_id": thread_id})
    db.session.commit()


def sql_get_section_name(section_id):
    sql = "SELECT name FROM sections WHERE id=:section_id"
    result = db.session.execute(sql, {"section_id": section_id})
    return result.fetchone()[0]


def sql_delete_thread(thread_id):
    sql = "DELETE FROM threads WHERE id=:thread_id RETURNING section_id"
    result = db.session.execute(sql, {"thread_id": thread_id})
    db.session.commit()
    return result.fetchone()


def sql_new_thread(section_id, creator_id, name):
    sql = "INSERT INTO threads (section_id, creator_id, name) " \
          "VALUES (:section_id, :creator_id, :name) RETURNING id"
    result = db.session.execute(sql, {"section_id": section_id, "creator_id": creator_id, "name": name})
    db.session.commit()
    return result.fetchone()


def sql_get_threads(section_id):
    user_id = users.user_id()
    user_role = users.user_role()
    sql = "SELECT T.id, T.name, " \
          "(SELECT COUNT(M.id) FROM messages M WHERE T.id=M.thread_id), U.username, " \
          "(T.creator_id=:user_id OR :user_role>0) " \
          "FROM users U, threads T " \
          "WHERE T.section_id=:section_id AND U.id=T.creator_id " \
          "ORDER BY T.id DESC"

    result = db.session.execute(sql, {"section_id": section_id, "user_id": user_id, "user_role": user_role})
    return result.fetchall()
