import random
import tornado.web
from flashcards.handlers import BaseHandler
from flashcards.models import UserFrame

class FrameMixin(object):

    def increment_frame_ids(self, first, increment=1):
        """Increments all the frame_ids from `first` by the given `increment`
        value.

        NOTE: this only works in it's currently state with sqlite as sqlite
        doesn't care about foreign keys."""

        # increment frame table
        for frame_id, in self.db.execute("SELECT frame_id FROM frames WHERE frame_id >= ? ORDER BY frame_id DESC", (first,)):
            self.db.execute("UPDATE frames set frame_id = frame_id + ? WHERE frame_id = ?", (increment, frame_id,))
        # increment primatives
        self.db.execute("UPDATE primatives set frame_id = frame_id + ? WHERE frame_id >= ?", (increment, first,))
        self.db.execute("UPDATE primatives set primative_id = primative_id + ? WHERE primative_id >= ?", (increment, first,))
        # increment user weights
        for frame_id, in self.db.execute("SELECT frame_id FROM user_card_weights_kanji WHERE frame_id >= ? ORDER BY frame_id DESC", (first,)):
            self.db.execute("UPDATE user_card_weights_kanji set frame_id = frame_id + ? WHERE frame_id = ?", (increment, frame_id,))
        for frame_id, in self.db.execute("SELECT frame_id FROM user_card_weights_keyword WHERE frame_id >= ? ORDER BY frame_id DESC", (first,)):
            self.db.execute("UPDATE user_card_weights_keyword set frame_id = frame_id + ? WHERE frame_id = ?", (increment, frame_id,))
        # update session data
        self.db.execute("UPDATE session_cards_kanji set frame_id = frame_id + ? WHERE frame_id >= ?", (increment, first,))
        self.db.execute("UPDATE session_cards_keyword set frame_id = frame_id + ? WHERE frame_id >= ?", (increment, first,))

    def delete_frame(self, frame_id):
        """removes a frame, and all references to it, and decrements the other
        frames larger than it by one"""

        self.db.execute("DELETE from frames WHERE frame_id = ?", (frame_id,))
        self.db.execute("DELETE from user_frame_weights WHERE frame_id = ?", (frame_id,))
        self.db.execute("DELETE from session_frames WHERE frame_id = ?", (frame_id,))
        self.db.execute("UPDATE frames set frame_id = frame_id - 1 WHERE frame_id > ?", (frame_id,))
        self.db.execute("UPDATE user_frame_weights set frame_id = frame_id - 1 WHERE frame_id > ?", (frame_id,))
        self.db.execute("UPDATE session_frames set frame_id = frame_id - 1 WHERE frame_id > ?", (frame_id,))
        # TODO: primatives

    def get_random_frame(self, session_type, exclude=None):
        """selects a random card from the user's cards"""

        if exclude:
            exclude = " AND frame_id NOT IN (%s)" % ', '.join([str(fid) for fid in exclude])
        else:
            exclude = ''

        # get weight sum
        total_weight, = self.db.execute(
            "SELECT SUM(weight) FROM user_card_weights_%s "
            "WHERE user_id = ? AND active = 1%s" % (session_type, exclude),
            (self.current_user.user_id,)).fetchone()

        # get all cards
        frames = self.db.execute(
            "SELECT frame_id, weight FROM user_card_weights_%s "
            "WHERE user_id = ? AND active = 1%s "
            "ORDER BY weight DESC, last_seen" % (session_type, exclude),
            (self.current_user.user_id,)).fetchall()

        # pick value
        target = random.randint(1, total_weight)

        # find matching card
        current = 0
        for frame_id, weight in frames:
            current += weight
            if current > target:
                return frame_id

        raise Exception("Unexpectedly found no card")

    def get_frame(self, frame_id):
        frame = self.db.execute(
            "SELECT frame_id, kanji, keyword_english, primative_english "
            "FROM frames "
            "WHERE frame_id = ?",
            (frame_id,)).fetchone()

        if frame:
            return dict(frame_id=frame_id, kanji=frame[1], keyword=frame[2], primative=frame[3])

        raise Exception("Couldn't find frame with id: %s" % frame_id)

    def get_user_frame(self, user_id, frame_id, session_type):
        card = self.db.execute(
            "SELECT user_id, frame_id, weight, last_seen, success_count, failure_count, active "
            "FROM user_card_weights_%s "
            "WHERE user_id = ? AND frame_id = ?" % session_type,
            (user_id, frame_id)).fetchone()
        if card:
            return UserFrame(*card)
        return None


class FrameHandler(BaseHandler, FrameMixin):
    @tornado.web.authenticated
    def get(self):
        rows = self.db.execute(
            "SELECT frame_id, kanji, keyword_english, primative_english "
            "FROM frames "
            "ORDER BY frame_id"
        ).fetchall()
        frames = []
        for frame_id, kanji, keyword_english, primative_english in rows:
            primatives = self.db.execute(
                "SELECT f.frame_id, f.kanji "
                "FROM primatives AS p JOIN frames AS f "
                "ON p.primative_id = f.frame_id "
                "WHERE p.frame_id = ? "
                "ORDER BY p.frame_id",
                (frame_id,)
            ).fetchall()
            primatives = {primative_id: primative_kanji for primative_id, primative_kanji in primatives}
            frames.append(
                dict(frame_id=frame_id, kanji=kanji, keyword=keyword_english, primative=primative_english,
                     primatives=primatives))
        self.write(dict(frames=frames))

    @tornado.web.authenticated
    def post(self):
        frame_id = self.get_argument("frame_id", None)
        kanji = self.get_argument("kanji")
        keyword = self.get_argument("keyword")
        primative = self.get_argument("primative")
        primatives = set()
        for p in self.get_arguments("primatives"):
            if not p.isdigit():
                raise tornado.web.HTTPError(400)
            primatives.add(int(p))
        if frame_id:
            if not frame_id.isdigit():
                raise tornado.web.HTTPError(400)
            frame_id = int(frame_id)
            # increment any existing frame ids equal to this one
            self.increment_frame_ids(frame_id)
            self.db.execute(
                "INSERT INTO frames (frame_id, kanji, keyword_english, primative_english) "
                "VALUES (?, ?, ?, ?)",
                (frame_id, kanji, keyword, primative))
        else:
            cursor = self.db.execute(
                "INSERT INTO frames (kanji, keyword_english, primative_english) "
                "VALUES (?, ?, ?)",
                (kanji, keyword, primative))
            frame_id = cursor.lastrowid
        frame = dict(frame_id=frame_id, kanji=kanji, keyword=keyword, primative=primative,
                     primatives={})
        for part_id in primatives:
            # make sure a primative with the given id actually exists
            part = self.db.execute("SELECT frame_id, kanji, keyword_english, primative_english "
                                   "FROM frames WHERE frame_id = ?", (part_id,)).fetchone()
            if part is None:
                raise tornado.web.HTTPError(400)
            self.db.execute(
                "INSERT INTO primatives (frame_id, primative_id) "
                "VALUES (?, ?)",
                (frame_id, part_id))
            frame['primatives'][part_id] = part[1]
        self.db.commit()
        self.write(frame)

class SingleFrameHandler(BaseHandler, FrameMixin):

    @tornado.web.authenticated
    def put(self, frame_id):
        frame_id = int(frame_id)
        frame = self.db.execute(
            "SELECT kanji, keyword_english, primative_english FROM frames WHERE frame_id = ?",
            (frame_id,)).fetchone()
        if not frame:
            raise tornado.web.HTTPError(404)
        kanji, keyword, primative = frame
        new_frame_id = self.get_argument("new_frame_id", str(frame_id))
        kanji = self.get_argument("kanji", kanji)
        keyword = self.get_argument("keyword", keyword)
        primative = self.get_argument("primative", primative)
        primatives = set()
        for p in self.get_arguments("primatives"):
            if not p.isdigit():
                raise tornado.web.HTTPError(400)
            primatives.add(int(p))
        if new_frame_id.isdigit():
            new_frame_id = int(new_frame_id)
        if new_frame_id != frame_id:
            # don't allow changes to the frame id in a put yet
            # TODO: ... this probably needs to happen in a different method
            # e.g. a "swap" style call
            raise tornado.web.HTTPError(400)
        else:
            self.db.execute(
                "UPDATE frames SET kanji = ?, keyword_english = ?, primative_english = ? "
                "WHERE frame_id = ?",
                (kanji, keyword, primative, frame_id))
        frame = dict(frame_id=frame_id, kanji=kanji,
                     keyword=keyword, primative=primative,
                     primatives={})
        old_primatives = {
            p[0]: p for p in
            self.db.execute("SELECT p.primative_id, f.kanji "
                            "FROM primatives AS p "
                            "JOIN frames AS f ON p.primative_id = f.frame_id "
                            "WHERE p.frame_id = ?", (frame_id,)).fetchall()}
        for part_id in primatives:
            # make sure a primative with the given id actually exists
            part = self.db.execute("SELECT frame_id, kanji, keyword_english, primative_english "
                                   "FROM frames WHERE frame_id = ?", (part_id,)).fetchone()
            if part is None:
                raise tornado.web.HTTPError(400)
            if part_id in old_primatives:
                part = old_primatives.pop(part_id)
            else:
                self.db.execute(
                    "INSERT INTO primatives (frame_id, primative_id) "
                    "VALUES (?, ?)",
                    (frame_id, part_id))
            frame['primatives'][part_id] = part[1]
        # clean up old primatives
        for part_id, kanji in old_primatives.values():
            self.db.execute(
                "DELETE FROM primatives WHERE frame_id = ? AND primative_id = ?",
                (frame_id, part_id))
        self.db.commit()
        self.write(frame)

    @tornado.web.authenticated
    def delete(self, frame_id):
        frame_id = int(frame_id)
        self.delete_frame(frame_id)
        self.db.commit()
