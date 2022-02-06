from db import db


def new_thread(section_id, creator_id, name):
    sql = "INSERT INTO threads (section_id, creator_id, name) " \
          "VALUES (:section_id, :creator_id, :name) RETURNING id"
    result = db.session.execute(sql, {"section_id": section_id, "creator_id": creator_id, "name": name})
    db.session.commit()
    return result.fetchone()


def get_threads(section_id):
    sql = "SELECT T.id, T.name, " \
          "(SELECT COUNT(M.id) FROM messages M WHERE T.id=M.thread_id) " \
          "FROM threads T WHERE T.section_id=" + str(section_id)

    result = db.session.execute(sql)
    return result.fetchall()
