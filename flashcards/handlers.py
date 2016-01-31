import sqlite3
import tornado.escape
import tornado.web
import traceback

from flashcards.settings import SQLITE_DBNAME
from flashcards.utils import force_unicode

from flashcards.models import User

class BaseHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = sqlite3.connect(SQLITE_DBNAME)
        return self._db

    def on_finish(self):
        if hasattr(self, '_db'):
            self._db.close()
            del self._db

    def get_current_user(self):
        user_id = self.get_secure_cookie("token")
        if not user_id:
            return None
        req = self.db.execute("SELECT user_id, username, name FROM users WHERE user_id = ?", (int(user_id),))
        user = req.fetchone()
        if user:
            return User(user_id=user[0], username=user[1], name=user[2])
        return None

    def prepare(self):
        """Puts any json data into self.request.arguments"""
        if any(('application/json' in x for x in self.request.headers.get_list('Content-Type'))):
            # ignore if there's no body to decode
            if self.request.body == '':
                return
            try:
                self._json_data = json_data = tornado.escape.json_decode(self.request.body)
            except ValueError:
                raise tornado.web.HTTPError(400, reason="Invalid JSON structure.")
            if type(json_data) != dict:
                raise tornado.web.HTTPError(400, reason="We only accept key value objects!")
            for key, value in json_data.items():
                if isinstance(value, dict):
                    continue
                if not isinstance(value, list):
                    value = [value]
                # get_arguments always expects a unicode value, so will fail
                # if given anything else
                self.request.arguments[key] = [force_unicode(v) for v in value if v is not None]

    def get_json_argument(self, name, default=tornado.web.RequestHandler._ARG_DEFAULT, strip=True):
        if not hasattr(self, '_json_data'):
            raise tornado.web.HTTPError(400, reason="Expected JSON request data")
        if not isinstance(name, (list, tuple)):
            name = [name]
        obj = self._json_data
        keychain = []
        for key in name:
            keychain.append(key)
            if key in obj:
                obj = obj[key]
            else:
                if default is self._ARG_DEFAULT:
                    raise tornado.web.MissingArgumentError('.'.join(keychain))
                else:
                    return default
        return obj

    def write_error(self, status_code, **kwargs):
        """Overrides tornado's default error writing handler to return json data instead of a html template"""
        rval = dict(code=status_code, message=self._reason)
        # if we're in debug mode, add the exception data to the response
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            rval['exc_info'] = traceback.format_exception(*kwargs["exc_info"])
        self.write(rval)
        self.finish()

class InitMixin(object):
    def get_init_data(self, user):
        return dict(user=user._asdict())

class InitHandler(BaseHandler, InitMixin):
    def get(self):
        self.xsrf_token
        if not self.current_user:
            self.write(dict())
        else:
            self.write(self.get_init_data(self.current_user))
