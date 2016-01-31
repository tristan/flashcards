-- the type of a concept, e.g. noun, verb, adjective, idiom, clause, kanji, kana, etc.
CREATE TABLE IF NOT EXISTS tags (
    tag_id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

-- card face combinations
CREATE TABLE IF NOT EXISTS frames (
    frame_id INTEGER PRIMARY KEY,
    kanji TEXT,
    keyword_english TEXT,
    primative_english TEXT,
    strokes INTEGER
);

-- links frames together to match a kanji's primatives
CREATE TABLE IF NOT EXISTS primatives (
    frame_id INTEGER,
    primative_id INTEGER,
    PRIMARY KEY(frame_id, primative_id)
);

-- users
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    name TEXT,
    picture BLOB
);

CREATE TABLE IF NOT EXISTS user_frame_weights (
    user_id INTEGER NOT NULL REFERENCES users (user_id) ON DELETE CASCADE,
    frame_id INTEGER NOT NULL REFERENCES frames (frame_id) ON DELETE CASCADE,
    -- the weight of the frame for the user
    weight INTEGER NOT NULL DEFAULT 1048576,
    -- the time the frame was last seen
    last_seen INTEGER DEFAULT 0,
    -- count the number of times the user has gotten this frame right or wrong
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    -- whether or not the frame is active, i.e. if it should be displayed to the
    -- user.
    active INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY(user_id, frame_id)
);

-- session data
CREATE TABLE IF NOT EXISTS sessions (
    session_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users (user_id) ON DELETE CASCADE,
    -- the time the session started
    start_time INTEGER NOT NULL,
    -- the time the session ended
    end_time INTEGER
);

-- which frames the user saw and got wrong or right in the session
CREATE TABLE IF NOT EXISTS session_frames (
    session_frames_id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions (session_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users (user_id) ON DELETE CASCADE,
    frame_id INTEGER NOT NULL REFERENCES frames (frame_id) ON DELETE CASCADE,
    success INTEGER,
    time INTEGER NOT NULL
);
