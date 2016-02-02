import tornado.web
from flashcards.handlers import BaseHandler
from flashcards.api.frame import FrameMixin
import time
import math

WEIGHT_DEFAULT = 3325
WEIGHT_MULTIPLIER = 0.75

class SessionHandler(BaseHandler, FrameMixin):

    @tornado.web.authenticated
    def post(self):
        """Begins a new session"""

        session_type = self.get_argument('type')

        if session_type == 'kanji' or session_type == 'keyword':

            # initialise card weirds for the user
            self.db.execute(
                "INSERT INTO user_card_weights_%s (user_id, frame_id, weight) "
                "SELECT ?, frame_id, ? FROM frames WHERE NOT EXISTS "
                "(SELECT 1 FROM user_card_weights_%s WHERE user_id = ? AND user_card_weights_%s.frame_id = frames.frame_id)" % (session_type, session_type, session_type),
                (self.current_user.user_id, WEIGHT_DEFAULT, self.current_user.user_id))

        else:
            raise tornado.web.HTTPError(400)

        # create new session
        cursor = self.db.execute(
            "INSERT INTO sessions (user_id, start_time, type) VALUES (?, ?, ?)",
            (self.current_user.user_id, time.time(), session_type))
        session_id = cursor.lastrowid

        self.db.commit()
        frame = self.get_frame(self.get_random_frame(session_type))
        self.set_secure_cookie('session', '%s|%s' % (session_id, session_type))
        self.write(dict(session_id=session_id, frame=frame))

    @tornado.web.authenticated
    def put(self):
        """Updates the session referenced by the user's current session"""
        session_id = self.get_secure_cookie('session').decode()
        if not session_id:
            raise tornado.web.HTTPError(400, reason="no_session")
        session_id, session_type = session_id.split('|')
        session_id = int(session_id)
        frame_id = int(self.get_argument("frame_id"))
        success = self.get_argument("success").lower() == "true"
        frame = self.get_user_frame(self.current_user.user_id, frame_id, session_type)
        if frame:
            now = time.time()
            if success:
                weight = math.ceil(frame.weight * WEIGHT_MULTIPLIER)
                failure_count = frame.failure_count
                success_count = frame.success_count + 1
            else:
                weight = WEIGHT_DEFAULT
                failure_count = frame.failure_count + 1
                success_count = frame.success_count
            self.db.execute(
                "UPDATE user_card_weights_%s "
                "SET weight = ?, last_seen = ?, success_count = ?, failure_count = ? "
                "WHERE user_id = ? AND frame_id = ?" % session_type,
                (weight, now, success_count, failure_count,
                 self.current_user.user_id, frame_id))
            self.db.execute(
                "INSERT INTO session_cards_%s (session_id, user_id, frame_id, success, time) "
                "VALUES (?, ?, ?, ?, ?)" % session_type,
                (session_id, self.current_user.user_id, frame_id, success, now))
            self.db.commit()
        frame = self.get_frame(self.get_random_frame(session_type))
        self.write(dict(session_id=session_id, frame=frame))

    @tornado.web.authenticated
    def delete(self):
        session_id = self.get_secure_cookie('session').decode()
        if not session_id:
            raise tornado.web.HTTPError(400, reason="no_session")
        session_id, session_type = session_id.split('|')
        session_id = int(session_id)
        self.clear_cookie("session")
        self.db.execute(
            "UPDATE sessions SET end_time = ? "
            "WHERE session_id = ?",
            (time.time(), session_id))
        self.db.commit()
