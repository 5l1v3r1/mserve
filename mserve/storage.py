from mserve.auth import Auth
from mserve.music import Music
from config import config

import sqlite3

class Storage():

    def __init__(self):
        conn = sqlite3.connect(config['DATABASE'])
        self.auth = Auth(conn)
        self.music = Music(conn)

    def close(self):
        self.conn.close()
