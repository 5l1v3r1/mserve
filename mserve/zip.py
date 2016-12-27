import os
import os.path
from binascii import hexlify
from zipfile import ZipFile

def do_zip(in_paths, out_path, inner_name):
    with ZipFile(out_path, 'w') as z:
        for path in in_paths:
            salt = hexlify(os.urandom(2)).decode('ascii')
            name = os.path.join(inner_name, salt + os.path.basename(path))
            z.write(path, arcname=name)
