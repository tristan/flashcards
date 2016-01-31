import os
import pickle

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
HTML_PATH = os.path.join(BASE_PATH, "html")
STATIC_PATH = os.path.join(BASE_PATH, "static")
VENDOR_PATH = os.path.join(BASE_PATH, "vendor")

SQLITE_DBNAME = "database.db"

with open("secret.key", 'rb') as keyfile:
    COOKIE_SECRET = pickle.load(keyfile)
