from willitlink.base.graph import MultiGraph

def expand_file_name(graph, file_name):
    """Takes a file name and attempts to return a list of expansions based on actual project files

    A file name could match multiple project files.  The matching for files is based on suffix
    matching, so "db.o" will match "build/.../db/db.o" or "build/.../v8_db.o" but "db" will not
    match either.  If there is an exact match, only that will be returned even if it could match
    other things.  For example, a file name of "mongod" will just return "mongod" and not
    "build/.../mongod".

    Keyword Arguments:
    graph -- The MultiGraph that contains the dependency data about our build objects as well as a
             list of all files in the project
    file_name -- The name of the file that we are trying to expand.  Note that this may be the end
                 of a file name.  For example, "libmongocommon.a" and "mongocommon.a" will return
                 the same results, assuming all libraries start with "lib".
    """
    full_file_names = []
    for i in graph.files:
        # If this file name matches exactly just return it rather than matching others
        #
        # This is to resolve an infinite loop in the following case:
        #
        # def recursive(graph, file_name):
        #     full_filenames = expand_file_names(graph, file_name)
        #     for full_filename in full_filenames:
        #         recursive(full_filename)
        #
        # In this case imagine that "mongod" is the file name.  Then full_filenames will have
        # "build/.../mongod" AND "mongod" (since we currently copy our binaries from the build
        # directory to the root of the tree as part of the build).  This means that the recursive
        # call will pass "mongod" into full_filename, which will expand the array again, and so on.
        if i == file_name:
            full_file_names = [ file_name ]
            break
        if i.endswith(file_name):
            full_file_names.append(i)
    return full_file_names

def expand_file_names(graph, file_names):
    """Takes a file name or list of file names and attempts to return a list of expansions

    See the expand_file_name function.  This function is equivalent but can optionally take a list

    Keyword Arguments:
    graph -- The MultiGraph that contains the dependency data about our build objects as well as a
             list of all files in the project
    file_names -- The name of the file that we are trying to expand, or a list of file names that we
                  are trying to expand
    """
    full_file_names = []
    if isinstance(file_names, list):
        for file_name in file_names:
            full_file_names.extend(expand_file_name(graph, file_name))
    else:
        full_file_names.extend(expand_file_name(graph, file_names))
    return full_file_names

def expand_symbol_name(graph, symbol_name):
    """Takes a symbol name and attempts to return a list of expansions based on actual project symbols

    A symbol name could match multiple project symbols.  The matching is based on whether a symbol
    "contains" another symbol.

    Keyword Arguments:
    graph -- The MultiGraph that contains the dependency data about our build objects as well as a
             list of all files in the project
    symbol_name -- The name of the symbol that we are trying to expand
    """
    full_symbol_names = []
    for i in graph.symbols:
        # If this symbol name matches exactly just return it rather than matching others
        #
        # This is to resolve an infinite loop in the following case:
        #
        # def recursive(graph, symbol_name):
        #     full_symbol_names = expand_symbol_names(graph, symbol_name)
        #     for full_symbol_name in full_symbol_names:
        #         recursive(full_symbol_name)
        #
        # Imagine a case where symbol A is fully contained in symbol B.  This means that
        # expand_symbol_names will always return both of those symbols when symbol A is passed in,
        # and the function above will never terminate.
        if i == symbol_name:
            full_symbol_names = [ symbol_name ]
            break
        if symbol_name in i:
            full_symbol_names.append(i)
    return full_symbol_names

def expand_symbol_names(graph, symbol_names):
    """Takes a symbol name or list of symbol names and attempts to return a list of expansions

    See the expand_symbol_name function.  This function is equivalent but can optionally take a list

    Keyword Arguments:
    graph -- The MultiGraph that contains the dependency data about our build objects as well as a
             list of all files in the project
    symbol_names -- The name of the symbol or symbols that we are trying to expand
    """
    full_symbol_names = []
    if isinstance(symbol_names, list):
        for symbol_name in symbol_names:
            full_symbol_names.extend(expand_symbol_name(graph, symbol_name))
    else:
        full_symbol_names.extend(expand_symbol_name(graph, symbol_names))
    return full_symbol_names
