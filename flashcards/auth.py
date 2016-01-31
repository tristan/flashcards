import bcrypt
import tornado.escape
import tornado.web

from flashcards.handlers import BaseHandler, InitMixin
from flashcards.models import User

class SignupHandler(BaseHandler):
    def post(self):
        hashed_password = bcrypt.hashpw(
            tornado.escape.utf8(self.get_argument("password")),
            bcrypt.gensalt())
        cursor = self.db.execute(
            "INSERT INTO users (username, password_hash, name) "
            "VALUES (?, ?, ?)",
            (self.get_argument("username"), hashed_password, self.get_argument("name")))
        if cursor:
            self.db.commit()
            self.set_secure_cookie("token", str(cursor.lastrowid))

class LoginHandler(BaseHandler, InitMixin):
    def post(self):
        req = self.db.execute("SELECT user_id, password_hash, name FROM users WHERE username = ?",
                              (self.get_argument("username"),))
        user = req.fetchone()
        if not user:
            raise tornado.web.HTTPError(400, reason="no_such_username")
        user_id, password_hash, user_name = user
        hashed_password = bcrypt.hashpw(
            tornado.escape.utf8(self.get_argument("password")),
            tornado.escape.utf8(password_hash))
        if hashed_password == password_hash:
            self.set_secure_cookie("token", str(user_id))
            self.write(self.get_init_data(
                User(user_id=user_id, username=self.get_argument("username"), name=user_name)))
        else:
            raise tornado.web.HTTPError(400, reason="invalid_password")

class LogoutHandler(BaseHandler):
    def post(self):
        self.clear_cookie("token")
        self.write(dict())
