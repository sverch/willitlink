# Return object format:
#
# [{
#     'symbol' : '<name>',
#     'type' : 'dependency/definition',
#     'object' : '<name>',
#     'path' : {
#         '<object_name>' : '<object_parent>',
#         '<object_parent>' : '<object_parent_parent>',
#         ...
#     }
# },
# ...
# ]

def locate_symbol(g, symbol_name):
    symbol_info = []
    for containing_file in g.get('symbol_to_file_sources', symbol_name):
        for containing_archive in g.get('dependency_to_targets', containing_file):
            for next_containing_archive in g.get('dependency_to_targets', containing_archive):
                symbol_info.append({ 'symbol' : symbol_name,
                    'type' : 'dependency',
                    'object' : containing_file,
                    'path' : {
                        containing_file : containing_archive,
                        containing_archive : next_containing_archive
                        } })
    return symbol_info
