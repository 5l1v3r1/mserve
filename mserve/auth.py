import os
from binascii import hexlify


class Auth(object):

    def __init__(self, conn):
        self.conn = conn


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
