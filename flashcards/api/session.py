import tornado.web
from flashcards.handlers import BaseHandler
from flashcards.api.card import CardMixin
import time

class SessionHandler(BaseHandler, CardMixin):

    @tornado.web.authenticated
    def post(self):
        """Begins a new session"""

        # initialise card weirds for the user
        self.db.execute(
            "INSERT INTO user_card_weights (user_id, card_id) "
            "SELECT ?, card_id FROM cards WHERE NOT EXISTS "
            "(SELECT 1 FROM user_card_weights WHERE user_id = ? AND user_card_weights.card_id = cards.card_id)",
            (self.current_user.user_id, self.current_user.user_id))

        # create new session
        cursor = self.db.execute(
            "INSERT INTO sessions (user_id, start_time) VALUES (?, ?)",
            (self.current_user.user_id, time.time()))
        session_id = cursor.lastrowid

        self.db.commit()
        card = self.get_card(self.get_random_card())
        self.set_secure_cookie('session', str(session_id))
        self.write(dict(session_id=session_id, card=card))

    @tornado.web.authenticated
    def put(self):
        """Updates the session referenced by the user's current session"""
        session_id = self.get_secure_cookie('session')
        if not session_id:
            raise tornado.web.HTTPError(400, reason="no_session")
        session_id = int(session_id)
        card_id = int(self.get_argument("card_id"))
        success = self.get_argument("success").lower() == "true"
        card = self.get_user_card(self.current_user.user_id, card_id)
        if card:
            now = time.time()
            if success:
                weight = card.weight - 1
                failure_count = card.failure_count
                success_count = card.success_count + 1
            else:
                weight = 100
                failure_count = card.failure_count + 1
                success_count = card.success_count
            self.db.execute(
                "UPDATE user_card_weights "
                "SET weight = ?, last_seen = ?, success_count = ?, failure_count = ? "
                "WHERE user_id = ? AND card_id = ?",
                (weight, now, success_count, failure_count,
                 self.current_user.user_id, card_id))
            self.db.execute(
                "INSERT INTO session_cards (session_id, user_id, card_id, success, time) "
                "VALUES (?, ?, ?, ?, ?)",
                (session_id, self.current_user.user_id, card_id, success, now))
            self.db.commit()
        card = self.get_card(self.get_random_card())
        self.write(dict(session_id=session_id, card=card))

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
