import os.path

from mserve.app import app
import mserve.routes.music
import mserve.routes.admin


def in_dir(ref, fname):
    return os.path.join(
            os.path.dirname(os.path.realpath(ref)),
            fname
        )
