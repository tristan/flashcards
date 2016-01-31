import tornado.web
from flashcards.handlers import BaseHandler
from flashcards.api.frame import FrameMixin
import time
import math

WEIGHT_DEFAULT = 1048576

class SessionHandler(BaseHandler, FrameMixin):

    @tornado.web.authenticated
    def post(self):
        """Begins a new session"""

        # initialise card weirds for the user
        self.db.execute(
            "INSERT INTO user_frame_weights (user_id, frame_id, weight) "
            "SELECT ?, frame_id, ? FROM frames WHERE NOT EXISTS "
            "(SELECT 1 FROM user_frame_weights WHERE user_id = ? AND user_frame_weights.frame_id = frames.frame_id)",
            (self.current_user.user_id, WEIGHT_DEFAULT, self.current_user.user_id))

        # create new session
        cursor = self.db.execute(
            "INSERT INTO sessions (user_id, start_time) VALUES (?, ?)",
            (self.current_user.user_id, time.time()))
        session_id = cursor.lastrowid

        self.db.commit()
        frame = self.get_frame(self.get_random_frame())
        self.set_secure_cookie('session', str(session_id))
        self.write(dict(session_id=session_id, frame=frame))

    @tornado.web.authenticated
    def put(self):
        """Updates the session referenced by the user's current session"""
        session_id = self.get_secure_cookie('session')
        if not session_id:
            raise tornado.web.HTTPError(400, reason="no_session")
        session_id = int(session_id)
        frame_id = int(self.get_argument("frame_id"))
        success = self.get_argument("success").lower() == "true"
        frame = self.get_user_frame(self.current_user.user_id, frame_id)
        if frame:
            now = time.time()
            if success:
                weight = math.ceil(frame.weight / 2)
                failure_count = frame.failure_count
                success_count = frame.success_count + 1
            else:
                weight = WEIGHT_DEFAULT
                failure_count = frame.failure_count + 1
                success_count = frame.success_count
            self.db.execute(
                "UPDATE user_frame_weights "
                "SET weight = ?, last_seen = ?, success_count = ?, failure_count = ? "
                "WHERE user_id = ? AND frame_id = ?",
                (weight, now, success_count, failure_count,
                 self.current_user.user_id, frame_id))
            self.db.execute(
                "INSERT INTO session_frames (session_id, user_id, frame_id, success, time) "
                "VALUES (?, ?, ?, ?, ?)",
                (session_id, self.current_user.user_id, frame_id, success, now))
            self.db.commit()
        frame = self.get_frame(self.get_random_frame())
        self.write(dict(session_id=session_id, frame=frame))

    @tornado.web.authenticated
    def delete(self):
        session_id = self.get_secure_cookie('session')
        if not session_id:
            raise tornado.web.HTTPError(400, reason="no_session")
        session_id = int(session_id)
        self.clear_cookie("session")
        self.db.execute(
            "UPDATE sessions SET end_time = ? "
            "WHERE session_id = ?",
            (time.time(), session_id))
        self.db.commit()
