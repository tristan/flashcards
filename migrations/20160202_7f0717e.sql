BEGIN

ALTER TABLE user_frame_weights RENAME TO user_card_weights_kanji;
ALTER TABLE session_frames RENAME TO session_cards_kanji;
ALTER TABLE sessions ADD COLUMN type TEXT;
UPDATE sessions set type = 'kanji';

COMMIT
