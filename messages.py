import users
from db import db


def create_new_message(thread_id, message):
    user_id = users.user_id()
    if user_id == 0:
        return False
    sql = "INSERT INTO messages(thread_id, sender_id, sent_at, message) " \
          "VALUES (:thread_id, :sender_id, NOW(), :message)"
    db.session.execute(sql, {"thread_id": thread_id, "sender_id": user_id, "message": message})
    db.session.commit()
    return True


def get_messages(thread_id):
    sql = "SELECT sender_id, sent_at, message " \
          "FROM messages WHERE thread_id=:thread_id"
    result = db.session.execute(sql, {"thread_id": thread_id})
    return result.fetchall()


def edit_message(message_id, message):
    if not has_message_access(message_id):
        # No perm
        return False
    sql = "UPDATE messages SET message=:message " \
          "WHERE message_id=:message_id"
    db.session.execute(sql, {"message": message, "message_id": message_id})
    db.session.commit()
    return True


def delete_message(message_id):
    if not has_message_access(message_id):
        # No perm
        return False
    sql = "DELETE FROM messages WHERE message_id=:message_id"
    db.session.execute(sql, {"message_id": message_id})
    db.session.commit()
    return True


def has_message_access(message_id):
    if users.user_role() == 1:
        # Admin role -> true
        return True
    sql = "SELECT sender_id FROM messages " \
          "WHERE message_id=:message_id"
    result = db.session.execute(sql, {"message_id": message_id})
    # Check if original sender is same as current user
    return result == users.user_id()


def find(string):
    print("messages find")
    # todo
