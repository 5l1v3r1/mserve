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


    def regex(self, regex):
        r = re.compile(regex, re.IGNORECASE)
        albums = []
        q = 'select album.id, album.title, artist.name from album left join artist on album.artist = artist.id'
        for id, title, artist in self.conn.cursor().execute(q):
            print(title)
            if r.search(title) or r.search(artist):
                albums.append((id, title, artist))
        return albums


    def non_alpha_artists(self):
        q = "select id, name from artist where name not like '[^a-zA-Z]%'"
        return list(self.conn.cursor().execute(q))


    def alpha_artists(self, letter):
        if len(letter) != 1 or not (letter.isalpha() and letter.isupper()):
            raise Exception
        q = 'select id, name from artist where name like ? or name like ?'
        return list(self.conn.cursor().execute(q, (letter + '%', letter.lower() + '%')))


    def artist_stuff(self, artist_id):
        c = self.conn.cursor()
        name, = next(c.execute('select name from artist where id = ?', artist_id))
        return name, list(
            c.execute('select id, title from album where artist = ?', (album_id,))
            )


    def get_files(self, album_id):
        return list(
            map(
                lambda x: x[0],
                self.conn.cursor().execute('select path from file where album = ?', (album_id,))
                )
            )


    def get_album_desc(self, album_id):
        title, artist =  next(self.conn.cursor().execute('select title, artist from album where id = ?', (album_id,)))
        return '[{}] {}'.format(artist, title)


    def recache(self, music_root):
        c = self.conn.cursor()
        c.execute('delete from artist')
        c.execute('delete from album')
        c.execute('delete from file')
        done = 0
        for root, dirs, files in os.walk(music_root):
            if done == 100:
                break
            done += 1
            for f in files:
                try:
                    fname = os.path.join(root, f)
                    tags = mutagen.File(fname, easy=True)
                    album = tags['album'][0]
                    artist = tags['artist'][0]
                except Exception as e:
                    continue
                artist_existed = False
                try:
                    artist_id, = next(c.execute('select id from artist where name = ?', (artist,)))
                    artist_existed = True
                except StopIteration:
                    c.execute('insert into artist (name) values (?)', (artist,))
                    artist_id = c.lastrowid
                    sys.stderr.write('ARTIST ' + str(artist_id) + ': ' + artist + '\n')
                try:
                    if not artist_existed:
                        raise StopIteration()
                    album_id, = next(c.execute('select id from album where artist = ? and title = ?', (artist_id, album)))
                except StopIteration:
                    c.execute('insert into album (artist, title) values (?, ?)', (artist_id, album))
                    album_id = c.lastrowid
                    sys.stderr.write('ALBUM ' + str(album_id) + ': ' + album + ' - ' + artist + '\n')
                c.execute('insert into file (album, path) values (?, ?)', (album_id, fname))
        self.conn.commit()
