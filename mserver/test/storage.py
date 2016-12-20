from mserver.storage import Storage
from config import config

st = Storage(config['DATABASE'])
print(st.get_files(2010))
