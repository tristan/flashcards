import tornado.ioloop
import tornado.options
import tornado.web

from flashcards.handlers import InitHandler
from flashcards.auth import LoginHandler, LogoutHandler, SignupHandler
from flashcards.api.language import LanguageHandler
from flashcards.api.frame import FrameHandler, SingleFrameHandler
from flashcards.api.tag import TagHandler
from flashcards.api.session import SessionHandler
from flashcards.settings import COOKIE_SECRET, HTML_PATH, STATIC_PATH, VENDOR_PATH

def make_app(debug=False):
    routes = [
        # auth stuff
        (r"/init", InitHandler),
        (r"/login", LoginHandler),
        (r"/logout", LogoutHandler),
        (r"/signup", SignupHandler),
        # api stuff
        (r"/api/frame", FrameHandler),
        (r"/api/frame/(\d+)", SingleFrameHandler),
        (r"/api/tag", TagHandler),
        (r"/api/session", SessionHandler),
        # static files
        (r"/static/(.*)", tornado.web.StaticFileHandler, {
            "path": STATIC_PATH
        }),
        (r"/vendor/(.*)", tornado.web.StaticFileHandler, {
            "path": VENDOR_PATH
        }),
        # index (NOTE: () to always passes an empty string to the initialiser)
        (r"/().*", tornado.web.StaticFileHandler, {
            "path": HTML_PATH,
            "default_filename": "index.html"
        }),
    ]
    return tornado.web.Application(
        routes,
        # settings
        debug=debug,
        xsrf_cookies=True,
        cookie_secret=COOKIE_SECRET
    )

if __name__ == "__main__":
    tornado.options.define("debug", default=False, type=bool)
    tornado.options.parse_command_line()
    app = make_app(tornado.options.options.debug)
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
