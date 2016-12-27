import sqlite3
from mserve.auth import Auth
from mserve.music import Music

class Storage():

    def __init__(self, db_dir):
        self.conn = sqlite3.connect(db_dir)
        self.auth = Auth(self.conn)
        self.music = Music(self.conn)

    def close(self):
        self.conn.close()
