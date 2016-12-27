from mserve.storage import Storage
from config import config

st = Storage(config['DATABASE'])

for release, artist, title, year, genre in st.music.query(title_re='lo'):
    print(' | '.join((artist, title, str(year), genre)))
