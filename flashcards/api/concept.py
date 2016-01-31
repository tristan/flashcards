import tornado.web
from flashcards.handlers import BaseHandler

class ConceptHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        rows = self.db.execute(
            "SELECT concept_id, name, details "
            "FROM concepts "
            "ORDER BY name"
        ).fetchall()
        concepts = []
        for concept_id, name, details in rows:
            tags = self.db.execute(
                "SELECT c.tag_id, t.name "
                "FROM concept_tags AS c JOIN tags AS t "
                "ON c.tag_id = t.tag_id "
                "WHERE c.concept_id = ? "
                "ORDER BY t.name",
                (concept_id,)
            ).fetchall()
            tags = [tag_name for tag_id, tag_name in tags]
            faces = self.db.execute(
                "SELECT face_id, language_id, text, front_only, case_sensitive FROM faces "
                "WHERE concept_id = ?", (concept_id,)).fetchall()
            faces = {language_id: {"text": text, "front_only": bool(front_only), "case_sensitive": bool(case_sensitive)}
                     for face_id, language_id, text, front_only, case_sensitive in faces}
            concepts.append(
                dict(concept_id=concept_id, name=name, details=details, tags=tags, faces=faces))
        self.write(dict(concepts=concepts))

    @tornado.web.authenticated
    def post(self):
        name = self.get_argument("name")
        details = self.get_argument("details", None)
        tag_names = set(self.get_arguments("tags"))
        faces = self.get_json_argument("faces", dict())
        dbtags = self.db.execute(
            "SELECT tag_id, name FROM tags WHERE name IN ({0})".format(
                ', '.join('?' for _ in tag_names)),
            tuple(tag_names)).fetchall()
        tags = []
        for tag_id, tag_name in dbtags:
            tag_names.remove(tag_name)
            tags.append((tag_id, tag_name))
        for tag_name in tag_names:
            cursor = self.db.execute(
                "INSERT INTO tags (name) VALUES (?)",
                (tag_name,))
            tags.append((cursor.lastrowid, tag_name))
        cursor = self.db.execute(
            "INSERT INTO concepts (name, details) "
            "VALUES (?, ?)",
            (name, details))
        concept_id = cursor.lastrowid
        concept = dict(concept_id=concept_id, name=name, details=details, tags=[], faces=faces)
        for tag_id, tag_name in tags:
            self.db.execute(
                "INSERT INTO concept_tags (concept_id, tag_id) "
                "VALUES (?, ?)",
                (concept_id, tag_id))
            concept['tags'].append(tag_name)
        if faces:
            # add any faces
            for language_id, face in faces.items():
                cursor = self.db.execute(
                    "INSERT INTO faces (concept_id, language_id, text, front_only, case_sensitive) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (concept_id, int(language_id), face['text'],
                     int(face.get('front_only', False)),
                     int(face.get('case_sensitive', False))))
                face['face_id'] = cursor.lastrowid
            # auto generate cards from faces
            for frontface in faces.values():
                for backface in faces.values():
                    if frontface is backface or backface.get('front_only', False):
                        continue
                    self.db.execute(
                        "INSERT INTO cards (concept_id, face_id_1, face_id_2) "
                        "VALUES (?, ?, ?)",
                        (concept_id, frontface['face_id'], backface['face_id']))

        self.db.commit()
        self.write(concept)

class SpecificConceptHandler(BaseHandler):

    @tornado.web.authenticated
    def put(self, concept_id):
        concept_id = int(concept_id)
        concept = self.db.execute(
            "SELECT name, details FROM concepts WHERE concept_id = ?",
            (concept_id,)).fetchone()
        if not concept:
            raise tornado.web.HTTPError(404)
        name, details = concept
        name = self.get_argument("name", name)
        details = self.get_argument("details", details)
        tag_names = set(self.get_arguments("tags"))
        faces = self.get_json_argument("faces", dict())
        # filter out existing tags
        existing_tags = self.db.execute(
            "SELECT c.tag_id, t.name FROM concept_tags AS c "
            "JOIN tags AS t ON c.tag_id = t.tag_id").fetchall()
        removed_tags = []
        for tag_id, tag_name in existing_tags:
            if tag_name in tag_names:
                tag_names.remove(tag_name)
            else:
                removed_tags.append((tag_id, tag_name))
        # if there are removed tags
        if removed_tags:
            for tag_id, tag_name in removed_tags:
                existing_tags.remove((tag_id, tag_name))
                self.db.execute(
                    "DELETE from concept_tags "
                    "WHERE concept_id = ? and tag_id = ?",
                    (concept_id, tag_id))
        # if there are new tags
        if tag_names:
            dbtags = self.db.execute(
                "SELECT tag_id, name FROM tags WHERE name IN ({0})".format(
                    ', '.join('?' for _ in tag_names)),
                tuple(tag_names)).fetchall()
            tags = []
            for tag_id, tag_name in dbtags:
                tag_names.remove(tag_name)
                tags.append((tag_id, tag_name))
            for tag_name in tag_names:
                cursor = self.db.execute(
                    "INSERT INTO tags (name) VALUES (?)",
                    (tag_name,))
                tags.append((cursor.lastrowid, tag_name))
            for tag_id, tag_name in tags:
                self.db.execute(
                    "INSERT INTO concept_tags (concept_id, tag_id) "
                    "VALUES (?, ?)",
                    (concept_id, tag_id))
                existing_tags.append((tag_id, tag_name))
        if faces:
            existing_faces = self.db.execute(
                "SELECT face_id, language_id, text, front_only, case_sensitive FROM faces "
                "WHERE concept_id = ?", (concept_id,)).fetchall()
            for face_id, language_id, text, front_only, case_sensitive in existing_faces:
                if str(language_id) in faces:
                    face = faces[str(language_id)]
                    # check if face has been cleared
                    if not face.get('text', ''):
                        pass # TODO
                    elif face['text'] != text or \
                         face.get('front_only', False) != bool(front_only) or \
                         face.get('case_sensitive', False) != bool(case_sensitive):
                        self.db.execute(
                            "UPDATE faces SET text = ?, front_only = ?, case_sensitive = ? "
                            "WHERE face_id = ?",
                            (face['text'], int(face.get('front_only', False)),
                             int(face.get('case_sensitive', False)), face_id))
                    del faces[str(language_id)]
                else:
                    # face isn't there at all
                    pass # TODO
            # process any new faces
            for language_id, face in faces.items():
                language_id = int(language_id)
                front_only = int(face.get('front_only', False))
                case_sensitive = int(face.get('case_sensitive', False))
                text = face['text']
                cursor = self.db.execute(
                    "INSERT INTO faces (concept_id, language_id, text, front_only, case_sensitive) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (concept_id, language_id, text, front_only, case_sensitive))
                existing_faces.append((cursor.lastrowid, language_id, text, front_only, case_sensitive))
            # auto generate cards from faces
            existing_cards = self.db.execute(
                "SELECT face_id_1, face_id_2 FROM cards "
                "WHERE concept_id = ?", (concept_id,)).fetchall()
            for frontface in existing_faces:
                for backface in existing_faces:
                    # backface[3] == front_only
                    if frontface is backface or backface[3] or (frontface[0], backface[0]) in existing_cards:
                        continue
                    self.db.execute(
                        "INSERT INTO cards (concept_id, face_id_1, face_id_2) "
                        "VALUES (?, ?, ?)",
                        (concept_id, frontface[0], backface[0]))
        cursor = self.db.execute(
            "UPDATE concepts SET name = ?, details = ? "
            "WHERE concept_id = ?",
            (name, details, concept_id))
        concept = dict(concept_id=concept_id, name=name, details=details,
                       tags=[tag_name for _, tag_name in existing_tags])
        self.db.commit()
        self.write(concept)
