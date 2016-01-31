-- languages used
CREATE TABLE IF NOT EXISTS languages (
    language_id INTEGER PRIMARY KEY,
    name TEXT
);

-- the type of a concept, e.g. noun, verb, adjective, idiom, clause, kanji, kana, etc.
CREATE TABLE IF NOT EXISTS tags (
    tag_id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

-- used to associate different faces to a single concept
CREATE TABLE IF NOT EXISTS concepts (
   concept_id INTEGER PRIMARY KEY,
   name TEXT UNIQUE,
   details TEXT
);

CREATE TABLE IF NOT EXISTS concept_tags (
    concept_id INTEGER NOT NULL REFERENCES concepts (concept_id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags (tag_id) ON DELETE CASCADE
);

-- specific faces available for each card
CREATE TABLE IF NOT EXISTS faces (
    face_id INTEGER PRIMARY KEY,
    concept_id INTEGER NOT NULL REFERENCES concepts (concept_id) ON DELETE CASCADE,
    language_id INTEGER NOT NULL REFERENCES language (language_id) ON DELETE CASCADE,
    -- the text of the face
    text TEXT NOT NULL,
    -- whether this face can only be the front of a card
    front_only INTEGER DEFAULT 0,
    -- whether the text should be case sensitive
    case_sensitive INTEGER DEFAULT 0,
    -- extra data (json data)
    extra TEXT,
    UNIQUE(concept_id, language_id)
);

-- list of faces that contain references to other faces, e.g. verb 1 is used in clause 2
CREATE TABLE IF NOT EXISTS face_references (
    face_id_1 INTEGER REFERENCES faces (face_id) ON DELETE CASCADE,
    face_id_2 INTEGER REFERENCES faces (face_id) ON DELETE CASCADE,
    PRIMARY KEY(face_id_1, face_id_2)
);

-- card face combinations
CREATE TABLE IF NOT EXISTS cards (
    card_id INTEGER PRIMARY KEY,
    concept_id INTEGER NOT NULL REFERENCES concepts (concept_id) ON DELETE CASCADE,
    face_id_1 INTEGER NOT NULL REFERENCES faces (face_id) ON DELETE CASCADE,
    face_id_2 INTEGER NOT NULL REFERENCES faces (face_id) ON DELETE CASCADE
);

-- kinda like tags for cards, e.g. the card that matches the english word to the
-- german word could be part of a deck
CREATE TABLE IF NOT EXISTS decks (
    deck_id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS deck_cards (
    deck_id INTEGER NOT NULL REFERENCES decks (deck_id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL REFERENCES cards (card_id) ON DELETE CASCADE,
    PRIMARY KEY(deck_id, card_id)
);

-- users
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    name TEXT,
    picture BLOB
);

-- weights per card for the user
CREATE TABLE IF NOT EXISTS user_card_weights (
    user_id INTEGER NOT NULL REFERENCES users (user_id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL REFERENCES cards (card_id) ON DELETE CASCADE,
    -- the weight of the card for the user
    weight INTEGER NOT NULL DEFAULT 100,
    -- the time the card was last seen
    last_seen INTEGER DEFAULT 0,
    -- count the number of times the user has gotten this card right or wrong
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    -- whether or not the card is active, i.e. if it should be displayed to the
    -- user. cards are deactivated if the user unselects a previously selected
    -- language or group, or specifically disables the card
    active INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY(user_id, card_id)
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

-- which cards the user saw and got wrong or right in the session
CREATE TABLE IF NOT EXISTS session_cards (
    session_cards_id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions (session_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users (user_id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL REFERENCES cards (card_id) ON DELETE CASCADE,
    success INTEGER,
    time INTEGER NOT NULL
);
