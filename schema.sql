CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    -- role: 0 = user, 1 = admin
    role INTEGER
);

CREATE TABLE threads (
    id SERIAL PRIMARY KEY,
    name TEXT,
    -- hidden: 0 = false, 1 = true
    hidden INTEGER
);

CREATE TABLE hidden_threads_access (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    thread_id INTEGER REFERENCES threads
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER REFERENCES threads,
    sender_id INTEGER REFERENCES users,
    sent_at TIMESTAMP,
    message TEXT
);