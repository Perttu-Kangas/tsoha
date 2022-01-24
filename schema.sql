CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    password TEST,
    -- role: 0 = user, 1 = admin
    role INTEGER
);

CREATE TABLE sections (
    id SERIAL PRIMARY KEY,
    name TEXT,
    -- hidden: 0 = false, 1 = true
    hidden INTEGER
);

CREATE TABLE hidden_sections_access (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    section_id INTEGER REFERENCES sections
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES sections,
    sender_id INTEGER REFERENCES users,
    sent_at TIMESTAMP,
    message TEXT
);