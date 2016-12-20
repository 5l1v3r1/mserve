import sys
import os
import os.path
import re
from binascii import hexlify
import sqlite3
import mutagen


class Storage(object):

    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)


    def close(self):
        self.conn.close()


    def ls_auth(self):
        return list(self.conn.cursor().execute('select * from auth'))


    def mk_auth(self, password):
        self.conn.cursor().execute('insert into auth (password) values (?)', (password,))
        self.conn.commit()


    def rm_auth(self, id):
        self.conn.cursor().execute('delete from auth where id = ?', (id,))
        self.conn.commit()


    def redeem_auth(self, password):
        c = self.conn.cursor()
        it = c.execute('select id from auth where password = ? and key is null', (password,))
        try:
            (id,) = next(it)
            key = hexlify(os.urandom(8)).decode('ascii')
            c.execute('update auth set key = ? where id = ?', (key, id))
            self.conn.commit()
            return key
        except StopIteration:
            return None


    def check_auth(self, key):
        c = self.conn.cursor()
        it = c.execute('select id from auth where key = ?', (key,))
        try:
            next(it)
            return True
        except StopIteration:
            return False


    def search_albums(self, regex):
        r = re.compile(regex, re.IGNORECASE)
        albums = []
        for id, title, artist in self.conn.cursor().execute('select * from album'):
            if r.search(title) or r.search(artist):
                albums.append((id, title, artist))
        return albums


    def get_files(self, album_id):
        files = []
        for path, in self.conn.cursor().execute('select path from file where album = ?', (album_id,)):
            files.append(path)
        return files


    def get_album_desc(self, album_id):
        title, artist =  next(self.conn.cursor().execute('select title, artist from album where id = ?', (album_id,)))
        return '[{}] {}'.format(artist, title)


    def recache(self, music_root):
        c = self.conn.cursor()
        c.execute('delete from album')
        c.execute('delete from file')
        done = 0
        for root, dirs, files in os.walk(music_root):
            for f in files:
                try:
                    fname = os.path.join(root, f)
                    tags = mutagen.File(fname, easy=True)
                    album = tags['album'][0]
                    artist = tags['artist'][0]
                except Exception as e:
                    continue
                try:
                    id, = next(c.execute('select id from album where title = ? and artist = ?', (album, artist)))
                except StopIteration:
                    c.execute('insert into album (title, artist) values (?, ?)', (album, artist))
                    id = c.lastrowid
                    sys.stderr.write(str(id) + ': ' + album + ' - ' + artist + '\n')
                c.execute('insert into file (album, path) values (?, ?)', (id, fname))
        self.conn.commit()
