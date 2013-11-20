import os.path
from willitlink.base.shell import command


def data_collector(args):
    for fn in [ os.path.join(args.data_dir, args.data),
                os.path.join(args.data_dir, 'dep_graph.json'),
                os.path.join(args.data_dir, args.tree_name)]:
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
    tree = command('scons {0} --tree=all,prune all'.format(' '.join(args.scons)), 
                   cwd=args.mongo, 
                   capture=True)

    print('[wil]: checked out clean SCons files.')
    command('git checkout SConstruct', cwd=args.mongo)
    command('git checkout site_scons/libdeps.py', cwd=args.mongo)

    print('[wil]: gathering dependency information from SCons output.')


    with open(os.path.join(args.data_dir, args.tree_name), 'w') as f:
        f.writelines(tree['out'])
    
    ct = 0
    tree_data = tree['out'].split('\n')
    with open(os.path.join(args.data_dir, args.data), 'w') as f:
        for ln in tree_data:
            if ln.startswith('{'):
                ct += 1
                f.write(ln)
                f.write('\n')

    print('[wil]: collected {0} dependencies.'.format(ct))
    print('[wil]: data collection complete!'.format(ct))
