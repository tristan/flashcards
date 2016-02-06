import sqlite3
import math

from flashcards.settings import SQLITE_DBNAME
from flashcards.api.session import WEIGHT_DEFAULT, WEIGHT_MULTIPLIER

if __name__ == '__main__':
    db = sqlite3.connect(SQLITE_DBNAME)
    frames = {}
    # replay all the sessions to get the new weights
    for user_id, frame_id, success in db.execute("SELECT user_id, frame_id, success FROM session_cards_keyword ORDER BY time").fetchall():
        if frame_id not in frames:
            frames[frame_id] = WEIGHT_DEFAULT
        if success:
            frames[frame_id] = math.ceil(frames[frame_id] * WEIGHT_MULTIPLIER)
        else:
            frames[frame_id] = WEIGHT_DEFAULT
    for user_id, frame_id, weight in db.execute("SELECT user_id, frame_id, weight from user_card_weights_keyword").fetchall():
        if frame_id in frames:
            new_weight = frames[frame_id]
        else:
            new_weight = WEIGHT_DEFAULT
        db.execute("UPDATE user_card_weights_keyword set weight = ? WHERE user_id = ? AND frame_id = ?",
                   (new_weight, user_id, frame_id))
    db.commit()
    print("DONE!!!!")
