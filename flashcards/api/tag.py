import tornado.web
from flashcards.handlers import BaseHandler

class TagHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        req = self.db.execute("SELECT tag_id, name "
                              "FROM tags "
                              "ORDER BY name")
        rows = req.fetchall()
        self.write(dict(tags=[
            dict(name=name)
            for tag_id, name in rows
        ]))
