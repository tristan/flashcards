import tornado.web
from flashcards.handlers import BaseHandler

class LanguageHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        req = self.db.execute("SELECT language_id, name FROM languages ORDER BY name")
        rows = req.fetchall()
        self.write(dict(languages=[
            dict(language_id=language_id, name=name) for language_id, name in rows
        ]))

    @tornado.web.authenticated
    def post(self):
        name = self.get_argument("name")
        cursor = self.db.execute(
            "INSERT INTO languages (name) "
            "VALUES (?)",
            (name,))
        if cursor:
            self.db.commit()
            self.write(dict(language_id=cursor.lastrowid, name=name))
