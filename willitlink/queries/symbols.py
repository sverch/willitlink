from willitlink.base.graph import MultiGraph

def locate_symbol(g, symbol_name):
    for containing_file in g.get('symbol_to_file_sources', symbol_name):
        for containing_archive in g.get('dependency_to_targets', containing_file):
            print "..." + containing_file[-30:] + " [..." + containing_archive[-30:] + "]"
            for next_containing_archive in g.get('dependency_to_targets', containing_archive):
                print "[..." + next_containing_archive[-30:] + "]"
