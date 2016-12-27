from mserve.cache import *
from config import config
import sqlite3

conn = sqlite3.connect(config['DATABASE'])
cache_files(conn, config['MUSIC_ROOT'])
cache_releases(conn, 10)
conn.commit()
