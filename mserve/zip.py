import sys
import os
import os.path
from binascii import hexlify
from zipfile import ZipFile

def do_zip(in_paths, out_path, inner_name):
    with ZipFile(out_path, 'w') as z:
        for path in in_paths:
            salt = hexlify(os.urandom(3)).decode('ascii').upper()
            base = os.path.basename(path).split('.')
            if len(base) < 2:
                sys.stderr.write('!!! [zip] ' + path + '\n')
            out = '.'.join(base[:-1] + [salt, base[-1]])
            name = os.path.join(inner_name, out)
            z.write(path, arcname=name)
