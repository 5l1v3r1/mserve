import sys
import os
import os.path

from uuid import UUID

from queue import Queue
from threading import Thread, Lock
import time

import mutagen
import musicbrainzngs


def cache_files(conn, music_root):
    c = conn.cursor()
    c.execute('delete from files')
    go = 100
    for root, dirs, files in os.walk(music_root):
        go -= 1
        if not go:
            break
        for f in files:
            try:
                fname = os.path.join(root, f)
                tags = mutagen.File(fname, easy=True)
                if tags is None:
                    continue
            except Exception as e:
                continue
            try:
                track = UUID(tags['musicbrainz_trackid'][0])
                release = UUID(tags['musicbrainz_albumid'][0])
                genres = tags.get('genre', [])
                try:
                    next(c.execute('select 1 from files where track = ?', (track.bytes,)))
                except StopIteration:
                    c.execute('insert into files (track, release, path) values (?, ?, ?)', (track.bytes, release.bytes, fname))
                    sys.stderr.write(fname + '\n')
                for genre in genres:
                    try:
                        next(c.execute('select 1 from genres where release = ? and genre = ?', (release.bytes, genre)))
                    except StopIteration:
                        c.execute('insert into genres (release, genre) values (?, ?)', (release.bytes, genre))
            except KeyError as e:
                sys.stderr.write('!!! [' + str(e) + '] ' + fname + '\n')


def lookup_info(release):
    info = musicbrainzngs.get_release_by_id(str(release), includes=['artists', 'artist-credits'])['release']
    title = info.get('title')
    year = int(info['date'][:4]) if 'date' in info else None
    artists = []
    for a in info['artist-credit']:
        if a != ' / ' and 'name' in a['artist']:
            artists.append(a['artist']['name'])
    return title, year, artists


def cache_releases(conn, nthreads):

    musicbrainzngs.set_useragent('mserver', '0.1.0.0')
    c = conn.cursor()
    todo = Queue()
    done = Queue()

    for r, in c.execute('select distinct release from files where release not in (select id from releases)'):
        release = UUID(bytes=r)
        todo.put(release)

    def go():
        while not todo.empty():
            release = todo.get()
            info = lookup_info(release)
            done.put((release,) + info)
            todo.task_done()

    for _ in range(nthreads):
        Thread(target=go).start()

    ended = False
    def end():
        todo.join()
        nonlocal ended
        ended = True

    Thread(target=end).start()

    while not ended:
        while not done.empty():
            release, title, year, artists = done.get()
            print(release, title, year, artists)
            c.execute('insert into releases (id, title, year) values (?, ?, ?)', (release.bytes, title, year))
            for artist in artists:
                c.execute('insert into credits (release, artist) values (?, ?)', (release.bytes, artist))
        time.sleep(0)
