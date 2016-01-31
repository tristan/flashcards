import random

from flashcards.models import UserCard

class CardMixin(object):
    """Handles common session methods"""

    def get_random_card(self):
        """selects a random card from the user's cards"""

        # get weight sum
        total_weight, = self.db.execute(
            "SELECT SUM(weight) FROM user_card_weights "
            "WHERE user_id = ? AND active = 1",
            (self.current_user.user_id,)).fetchone()

        # get all cards
        cards = self.db.execute(
            "SELECT card_id, weight FROM user_card_weights "
            "WHERE user_id = ? AND active = 1 "
            "ORDER BY weight DESC, last_seen",
            (self.current_user.user_id,)).fetchall()

        # pick value
        target = random.randint(1, total_weight)

        # find matching card
        current = 0
        for card_id, weight in cards:
            current += weight
            if current > target:
                return card_id

        raise Exception("Unexpectedly found no card")

    def get_card(self, card_id):
        card = self.db.execute(
            "SELECT ffl.name, ff.text, ff.case_sensitive, "
            "bfl.name, bf.text, bf.case_sensitive "
            "FROM cards AS c JOIN faces AS ff ON c.face_id_1 = ff.face_id "
            "JOIN faces AS bf ON c.face_id_2 = bf.face_id "
            "JOIN languages AS ffl ON ff.language_id = ffl.language_id "
            "JOIN languages AS bfl ON bf.language_id = bfl.language_id "
            "WHERE c.card_id = ?",
            (card_id,)).fetchone()

        if card:
            return dict(
                card_id=card_id,
                front=dict(language=card[0], text=card[1], case_sensitive=bool(card[2])),
                back=dict(language=card[3], text=card[4], case_sensitive=bool(card[5])),
            )
        raise Exception("Couldn't find card with id: %s" % card_id)

    def get_user_card(self, user_id, card_id):
        card = self.db.execute(
            "SELECT user_id, card_id, weight, last_seen, success_count, failure_count, active "
            "FROM user_card_weights "
            "WHERE user_id = ? AND card_id = ?",
            (user_id, card_id)).fetchone()
        if card:
            return UserCard(*card)
        return None
