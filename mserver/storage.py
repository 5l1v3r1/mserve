from os import urandom
from binascii import hexlify
import sqlite3


class Storage(object):

    def __init__(self, path):
        self.conn = sqlite3.connect(path)


    def close(self):
        self.conn.close()


    def ls_auth(self):
        list(self.conn.cursor().execute('select * from auth'))


    def mk_auth(self, password):
        self.conn.cursor().execute('insert into auth (password) values ("{}")'.format(password))
        self.conn.commit()


    def rm_auth(self, id):
        self.conn.cursor().execute('delete from auth where id = {}'.format(id))
        self.conn.commit()


    def redeem_auth(self, password):
        c = self.conn.cursor()
        it = c.execute('select id from auth where password = "{}"'.format(password))
        try:
            (id,) = next(it)
            key = hexlify(urandom(8)).decode('ascii')
            c.execute('update auth set key = ("{}") where id = {}'.format(key, id))
            self.conn.commit()
            return key
        except StopIteration:
            return None


    def check_auth(self, key):
        c = self.conn.cursor()
        it = c.execute('select id from auth where key = "{}"'.format(key))
        try:
            next(it)
            return True
        except StopIteration:
            return False


    def search_albums(self, regex):
        pass


    def get_files(self, album_id):
        pass


    def recache(self, music_root):
        c = self.conn.cursor
        c.execute('delete from albums')
        pass
        self.conn.commit()
