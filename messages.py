from db import db


def new_message(thread_id, sender_id, message):
    sql = "INSERT INTO messages (thread_id, sender_id, sent_at, message) " \
          "VALUES (:thread_id, :sender_id, NOW(), :message)"
    db.session.execute(sql, {"thread_id": thread_id, "sender_id": sender_id, "message": message})
    db.session.commit()


def get_messages(thread_id):
    sql = "SELECT U.username, M.sent_at, M.message " \
          "FROM users U, messages M WHERE M.thread_id=:thread_id AND U.id=M.sender_id " \
          "ORDER BY M.id"

    result = db.session.execute(sql, {"thread_id": thread_id})
    return result.fetchall()
