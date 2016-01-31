import sqlite3
import math

from flashcards.settings import SQLITE_DBNAME

if __name__ == '__main__':
    db = sqlite3.connect(SQLITE_DBNAME)
    for user_id, frame_id, weight in db.execute("SELECT user_id, frame_id, weight from user_frame_weights").fetchall():
        new_weight = 1048576
        for i in range(100 - weight):
            new_weight = math.ceil(new_weight / 2)
        db.execute("UPDATE user_frame_weights set weight = ? WHERE user_id = ? AND frame_id = ?",
                   (new_weight, user_id, frame_id))
    db.commit()
    print("DONE!!!!")
