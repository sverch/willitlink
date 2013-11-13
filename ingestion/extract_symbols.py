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

# TODO: Use the python library to read elf files, so we know the file exists at this point
def get_symbols_used(object_file):
    if sys.platform.startswith('linux'):
        cmd = r'nm "' + object_file + r'" | grep -e "U " | c++filt'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        uses = p.communicate()[0].decode()

        # Linux prints some extra information at the beginning of each symbol line, so we need to
        # strip that out here
        return list_process([ use[19:]
                              for use in uses.split('\n')
                              if use != '' ])
    else:
        uses = subprocess.check_output("nm -u " + object_file + " | c++filt", shell=True)
        return list_process([ use.strip()
                              for use in uses.split('\n')
                              if use != '' ])

def get_symbols_defined(object_file):
    if sys.platform.startswith('linux'):
        cmd = r'nm "' + object_file + r'" | grep -v -e "U " | c++filt'
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        definitions = p.communicate()[0].decode()

        # Linux prints some extra information at the beginning of each symbol line, so we need to
        # strip that out here
        return list_process([ definition[19:]
                              for definition in definitions.split('\n')
                              if definition != '' ])
    else:
        definitions = subprocess.check_output("nm -jU " + object_file + " | c++filt", shell=True)
        return list_process([ definition.strip()
                              for definition in definitions.split('\n')
                              if definition != '' ])

def usage():
    print("Usage: " + sys.argv[0] + " file [defined/used (default=defined)]")

def main():
    extraction_type = "defined"
    object_file = ""

    if len(sys.argv) == 2:
        object_file = sys.argv[1]
    elif len(sys.argv) == 3:
        object_file = sys.argv[1]
        extraction_type = sys.argv[2]
        if extraction_type != "defined" and extraction_type != "used":
            usage()
            sys.exit(-1)
    else:
        usage()
        sys.exit(-1)

    # TODO: The file could still be deleted after this point, but we are using an external command
    # to get the symbols so we need to check here.
    if not os.path.exists(object_file):
        print("Error: \"" + object_file + "\" does not exist")
        usage()
        sys.exit(-1)

    if extraction_type == "defined":
        for symbol in get_symbols_defined(object_file):
            print(symbol)
    else:
        for symbol in get_symbols_used(object_file):
            print(symbol)

if __name__ == '__main__':
    main()
