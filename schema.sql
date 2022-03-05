CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    -- role: 0 = user, 1 = admin
    role INTEGER
);

CREATE TABLE sections (
    id SERIAL PRIMARY KEY,
    name TEXT,
    -- hidden: 0 = false, 1 = true
    hidden INTEGER
);

CREATE TABLE sections_access (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES sections ON DELETE CASCADE,
    user_id INTEGER REFERENCES users ON DELETE CASCADE
);

CREATE TABLE threads (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES sections ON DELETE CASCADE,
    creator_id INTEGER REFERENCES users ON DELETE CASCADE,
    name TEXT
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER REFERENCES threads ON DELETE CASCADE,
    sender_id INTEGER REFERENCES users ON DELETE CASCADE,
    sent_at TIMESTAMP(0),
    message TEXT
);

CREATE TABLE likes (
    id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages ON DELETE CASCADE,
    user_id INTEGER REFERENCES users ON DELETE CASCADE
);