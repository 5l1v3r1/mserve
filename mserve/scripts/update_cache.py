import sys
import sqlite3
from mserve.cache import cache_files, cache_releases

conn = sqlite3.connect(sys.argv[1])
cache_files(conn, sys.argv[2])
cache_releases(conn, 5)
conn.commit()
