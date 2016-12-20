import os.path
from flask import Flask, g
from mserver.storage import Storage
from config import config


app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(config)


def get_st():
    if not hasattr(g, 'storage'):
        g.storage = Storage(app.config['DATABASE'])
    return g.storage


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'storage'):
        g.storage.close()
