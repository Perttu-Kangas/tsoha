import users
from db import db


# THREADS START

def create_new_thread(title, message, hidden):
    print("messages create_new_thread")
    # todo


def get_threads():
    print("messages get_threads")
    # todo


def edit_thread(thread_id, new_title):
    print("messages edit_thread")
    # todo


def delete_thread(thread_id):
    print("messages delete_thread")
    # todo


# MESSAGES START

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
    return db.session.execute(sql, {"thread_id": thread_id})


def edit_message(message_id, new_context):
    print("messages edit_message")
    # todo


def delete_message(message_id):
    print("messages delete_message")
    # todo


def find(string):
    print("messages find")
    # todo
