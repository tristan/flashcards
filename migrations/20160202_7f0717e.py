import sqlite3
import math

from flashcards.settings import SQLITE_DBNAME

if __name__ == '__main__':
    db = sqlite3.connect(SQLITE_DBNAME)
    for user_id, frame_id, weight in db.execute("SELECT user_id, frame_id, weight from user_card_weights_kanji").fetchall():
        new_weight = max(3325, math.ceil(math.pow(1.5, math.log(weight, 2))))
        db.execute("UPDATE user_card_weights_kanji set weight = ? WHERE user_id = ? AND frame_id = ?",
                   (new_weight, user_id, frame_id))
    db.commit()
    print("DONE!!!!")
