CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    -- role: 0 = user, 1 = admin
    role INTEGER
);

CREATE INDEX idx_username ON users (username);

CREATE TABLE sections (
    id SERIAL PRIMARY KEY,
    name TEXT,
    -- hidden: 0 = false, 1 = true
    hidden INTEGER
);

CREATE TABLE sections_access (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES sections,
    user_id INTEGER REFERENCES users
);

CREATE TABLE threads (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES sections,
    creator_id INTEGER REFERENCES users,
    name TEXT
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER REFERENCES threads,
    sender_id INTEGER REFERENCES users,
    sent_at TIMESTAMP,
    message TEXT
);