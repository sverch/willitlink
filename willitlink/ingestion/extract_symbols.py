"""
Script to extract symbols from an object file

get_symbols_used("sock.o")

Get all symbols that sock.o requires to link properly (symbols that it uses but doesn't define)

get_symbols_defined("sock.o")

Get symbols provided by sock.o that other object files can link against
"""

import os
import sys
import subprocess

def list_process(items):
    r = []

    for l in items:
        if isinstance(l, list):
            for i in l:
                if i.startswith('.L'):
                    continue
                else:
                    r.append(str(i))
        else:
            if l.startswith('.L'):
                continue
            else:
                r.append(str(l))

    return r

def get_symbol_worker(object_file, platform, task):
    if platform == 'linux':
        if task == 'used':
            cmd = r'nm "' + object_file + r'" | grep -e "U " | c++filt'
        elif task == 'defined':
            cmd = r'nm "' + object_file + r'" | grep -v -e "U " | c++filt'
    elif platform == 'darwin':
        if task == 'used':
            cmd = "nm -u " + object_file + " | c++filt"
        elif task == 'defined':
            cmd = "nm -jU " + object_file + " | c++filt"

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    uses = p.communicate()[0].decode()

    if platform == 'linux':
        return list_process([ use[19:]
                              for use in uses.split('\n')
                              if use != '' ])
    elif platform == 'darwin':
        return list_process([ use.strip()
                              for use in uses.split('\n')
                              if use != '' ])



# TODO: Use the python library to read elf files, so we know the file exists at this point
def get_symbols_used(object_file, mongo_path):
    object_file = os.path.join(mongo_path, object_file)

    platform = 'linux' if sys.platform.startswith('linux') else 'darwin'

    return get_symbol_worker(object_file, platform, task='used')


def get_symbols_defined(object_file, mongo_path):
    object_file = os.path.join(mongo_path, object_file)

    platform = 'linux' if sys.platform.startswith('linux') else 'darwin'

    return get_symbol_worker(object_file, platform, task='defined')
