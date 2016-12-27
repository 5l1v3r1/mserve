from mserver.storage import Storage

st = Storage()

for release, title, year, artists in st.music.query(title_re='lo'):
    print(title, artists)
