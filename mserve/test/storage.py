from mserve.storage import Storage
from config import config

import musicbrainzngs

st = Storage(config['DATABASE'])
print(st.get_files(2010))
