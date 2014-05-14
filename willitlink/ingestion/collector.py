import os.path

import re

from willitlink.base.shell import command
from willitlink.base.dev_tools import Timer

def data_collector(args):
    # Output of scons dependency tree
    tree_output = os.path.join(args.data, 'dependency_tree.txt')

    # Output from our libdeps patch
    libdeps_output = os.path.join(args.data, 'deps.json')

    for fn in [ libdeps_output,
                os.path.join(args.data, 'dep_graph.json'),
                tree_output ]:
        if os.path.exists(fn):
            os.remove(fn)

    print('[wil]: cleaned up previous artifacts.')

    command('git checkout SConstruct', cwd=args.mongo)
    command('git checkout site_scons/libdeps.py', cwd=args.mongo)
    print('[wil]: checked out clean SCons files.')

    patch_path = os.path.join(args.cwd, 'assets', 'print_scons_libdeps.patch')
    command('git apply {0}'.format(patch_path), cwd=args.mongo)
    print('[wil]: applied patch to SCons file.')

    print('[wil]: running SCons all build.')
    with Timer('running scons', args.timers):
        tree = command('scons {0} --tree=all,prune all'.format(' '.join(args.scons)),
                       cwd=args.mongo,
                       capture=True)

    print('[wil]: checked out clean SCons files.')
    command('git checkout SConstruct', cwd=args.mongo)
    command('git checkout site_scons/libdeps.py', cwd=args.mongo)

    print('[wil]: gathering dependency information from SCons output.')

    if not os.path.exists(args.data):
        os.mkdir(args.data)

    with open(tree_output, 'w') as f:
        with Timer('writing data to ' + tree_output, args.timers):
            f.writelines(tree['out'])

    ct = 0
    tree_data = tree['out'].split('\n')
    dep_object_regex = re.compile("^({.*}).*")
    with open(libdeps_output, 'w') as f:
        with Timer('filtering out dep info from scons output', args.timers):
            for ln in tree_data:
                m = dep_object_regex.search(ln)
                if m is not None:
                    ct += 1
                    f.write(m.group(1))
                    f.write('\n')

    print('[wil]: collected {0} dependencies.'.format(ct))
    print('[wil]: data collection complete!')
