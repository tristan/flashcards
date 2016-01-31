-- migration for database @ ae70975

CREATE TEMP TABLE IF NOT EXISTS _variables (name TEXT PRIMARY KEY, value TEXT);

-- update these to match ids
INSERT OR REPLACE INTO _variables VALUES ('jap_lang_id', 3);
INSERT OR REPLACE INTO _variables VALUES ('eng_lang_id', 2);

-- create frames by combining concepts and faces
INSERT INTO frames (kanji, keyword_english)
        SELECT j.text, e.text FROM concepts AS c
        JOIN faces AS j ON c.concept_id = j.concept_id AND j.language_id = (SELECT value FROM _variables WHERE name = 'jap_lang_id')
        JOIN faces AS e ON c.concept_id = e.concept_id AND e.language_id = (SELECT value FROM _variables WHERE name = 'eng_lang_id')    ;

CREATE TEMP TABLE IF NOT EXISTS _card_to_frame (
        card_id INTEGER,
        frame_id INTEGER,
        PRIMARY KEY (card_id, frame_id)
);

INSERT INTO _card_to_frame
        SELECT cd.card_id, fr.frame_id FROM cards AS cd
        JOIN faces AS j ON cd.face_id_1 = j.face_id
        JOIN faces AS e ON cd.face_id_2 = e.face_id
        JOIN frames AS fr ON fr.kanji = j.text AND fr.keyword_english = e.text
;

INSERT INTO user_frame_weights
       SELECT u.user_id, cf.frame_id, u.weight, u.last_seen, u.success_count, u.failure_count, u.active
       FROM user_card_weights AS u
       JOIN _card_to_frame AS cf ON u.card_id = cf.card_id
;

INSERT INTO session_frames (session_id, user_id, frame_id, success, time)
       SELECT sc.session_id, sc.user_id, cf.frame_id, sc.success, sc.time
       FROM session_cards AS sc
       JOIN _card_to_frame AS cf ON sc.card_id = cf.card_id
;

DROP TABLE session_cards;
DROP TABLE user_card_weights;
DROP TABLE deck_cards;
DROP TABLE decks;
DROP TABLE cards;
DROP TABLE face_references;
DROP TABLE faces;
DROP TABLE concept_tags;
DROP TABLE concepts;
DROP TABLE languages;
