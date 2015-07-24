#!/usr/bin/env python3

import os
import subprocess
import re
import shutil
import sys

# print(out)

'''
$ ldd /bin/ls
        linux-vdso.so.1 (0x00007ffe80f96000)
        libselinux.so.1 => /lib/x86_64-linux-gnu/libselinux.so.1 (0x00007fbaa28c4000)
        libacl.so.1 => /lib/x86_64-linux-gnu/libacl.so.1 (0x00007fbaa26bb000)
        libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fbaa2311000)
        libpcre.so.3 => /lib/x86_64-linux-gnu/libpcre.so.3 (0x00007fbaa20a3000)
        libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007fbaa1e9f000)
        /lib64/ld-linux-x86-64.so.2 (0x00007fbaa2b0f000)
        libattr.so.1 => /lib/x86_64-linux-gnu/libattr.so.1 (0x00007fbaa1c99000)
        libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007fbaa1a7c000)
'''

regex = re.compile('(?P<basename>[^ ]+) (=> (?P<path>[^ ]+) )?(\((?P<addr>0x[a-f0-9]+)\))$')

def find_libs(path):
    out = subprocess.check_output(['/usr/bin/ldd', path], universal_newlines=True)

    for line in out.split('\n'):
        line = line.strip()
        if not line:
            continue

        if line == 'statically linked':
            return

        match = regex.match(line).groupdict()

        if line.startswith('linux-vdso.so.1'):
            continue

        if not match:
            continue

        path = match['path']

        basename = match['basename']

        if not path:
            path = basename
            basename = os.path.basename(basename)

        if not basename in libs:
            libs[basename] = path

        if not basename in checked:
            unchecked.append(path)

def usage():
    print('usage: {} <file> [--copy destination]'.format(sys.argv[0]))

if __name__ == '__main__':
    try:
        f = sys.argv[1]
    except IndexError:
        usage()
        exit(-1)

    copy = False
    try:
        copy = sys.argv[sys.argv.index('--copy') + 1]
    except ValueError:
        pass
    except IndexError:
        if not 'DESTDIR' in os.environ:
            usage()
            exit(-2)
        copy = os.environ['DESTDIR']
        pass

    libs = {}
    checked = []
    unchecked = [f]

    while unchecked:
        lib = unchecked.pop()
        checked.append(lib)
        find_libs(lib)

    print(libs)

    if copy:
        for name, path in libs.items():

            # import ipdb; ipdb.set_trace()
            dest = os.path.join(copy, path[1:])
            os.makedirs(os.path.dirname(dest), mode=0o755, exist_ok=True)
            shutil.copyfile(path, dest)
