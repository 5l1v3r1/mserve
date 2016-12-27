import re
from uuid import UUID

class Music(object):

    def __init__(self, conn):
        self.conn = conn


    def has(self, release):
        try:
            next(self.conn.cursor().execute('select 1 from releases where id = ?', (release.bytes,)))
            return True
        except StopIteration:
            return False


    def files_of(self, release):
        return [
            path
            for path,
            in self.conn.cursor().execute('select path from files where release = ?', (release.bytes,))
            ]


    def artists_of(self, release):
        return [
            artist
            for artist,
            in self.conn.cursor().execute('select artist from credits where release = ?', (release.bytes,))
            ]


    def genres_of(self, release):
        return [
            genre
            for genre,
            in self.conn.cursor().execute('select genre from genres where release = ?', (release.bytes,))
            ]


    def fmt_desc(self, title, year, artists):
        return '[{}] {} [{}]'.format(' + '.join(artists), title, year)


    def describe(self, release):
        title, year = next(self.conn.cursor().execute('select title, year from releases where id = ?', (release.bytes,)))
        artists = self.artists_of(release)
        return self.fmt_desc(title, year, artists)


    def query(self, title_re=None, year_from=None, year_to=None, artist_re=None, genre_re=None):

        # Obviously this is dumb if you have a lot of music.
        # With a large enough collection, more parameters would have to be
        # incorporated into the sql query itself.
        extra = ' and '.join(
                filter(None, [
                        None if year_from is None else '? <= year',
                        None if year_to is None else 'year <= ?'
                    ]
                )
            )
        q = ' where '.join(filter(None, ['select * from releases', extra]))
        params = tuple(filter(None, [year_from, year_to]))

        results = []

        for r, title, year in self.conn.execute(q, params):

            release = UUID(bytes=r)

            if title_re is not None:
                if not re.search(title_re, title, re.I):
                    continue

            artists = self.artists_of(release)
            if artist_re is not None:
                ar = re.compile(artist_re, re.I)
                match = False
                for artist in artists:
                    if ar.search(artist):
                        match = True
                        break
                if not match:
                    continue

            genres = self.genres_of(release)
            if genre_re is not None:
                gr = re.compile(genre_re, re.I)
                match = False
                for genre in genres:
                    if gr.search(genre):
                        match = True
                        break
                if not match:
                    continue

            results.append({
                'id': release,
                'artist': ' + '.join(artists),
                'title': title,
                'year': year,
                'genre': '/'.join(genres),
                })

        results.sort(key=lambda x: (x['artist'].upper(), x['title'].upper(), x['year']))
        return results
