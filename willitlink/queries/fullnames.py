from willitlink.base.graph import MultiGraph

# TODO: Do this in a smarter way.  This function's purpose is to basically clean
# up names from the user, so that they can type libmongocommon.a rather than the
# full path.

# TODO: Doing queries on things like "mongod" result in an infinite loop, since
# multiple targets end with "mongod"
#
# How you ask?  (I had forgotten why I wrote this comment so I had the same question)  Consider the
# following in a recursive call:
#
# def recursive(g, file_name):
#     full_filenames = get_full_filenames(g, file_name)
#     for full_filename in full_filenames:
#         recursive(full_filename)
#
# It may not seem bad at first, but imagine that "mongod" is the file name.  Then full_filenames
# will have "build/.../mongod" AND "mongod" (since we currently copy our binaries to the root of the
# tree as part of the build).  This means that the recursive call will pass "mongod" into
# full_filename, which will expand the array again, and so on.  Even if the right answer is to just
# make sure the callers of this function don't call it in recursive calls, I think this is a good
# comment to leave as a warning.

def get_full_filenames(g, file_names):

    full_file_names = []

    if isinstance(file_names, list):
        for i in g.files:
            for file_name in file_names:
                # If we have an exact match just return a single element to reduce noise
                # TODO: find a more elegant way to do this and document how it works.
                if i == file_name:
                    full_file_names.append(file_name)
                    break
                if i.endswith(file_name):
                    full_file_names.append(i)
    else:
        for i in g.files:
            # If we have an exact match just return a single element to reduce noise
            # TODO: find a more elegant way to do this and document how it works.
            if i == file_names:
                full_file_names = [ file_names ]
                break
            if i.endswith(file_names):
                full_file_names.append(i)


    return full_file_names

# XXX: This suffers from all the same problems as the funtion above since I just copy pasted.
# Should fix these both at the same time in a refactor.

def get_full_symbol_names(g, symbol_names):

    full_symbol_names = []

    if isinstance(symbol_names, list):
        for i in g.files:
            for file_name in symbol_names:
                # If we have an exact match just return a single element to reduce noise
                # TODO: find a more elegant way to do this and document how it works.
                if i == file_name:
                    full_symbol_names.append(file_name)
                    break
                if i.contains(file_name):
                    full_symbol_names.append(i)
    else:
        for i in g.files:
            # If we have an exact match just return a single element to reduce noise
            # TODO: find a more elegant way to do this and document how it works.
            if i == symbol_names:
                full_symbol_names = [ symbol_names ]
                break
            if i.contains(symbol_names):
                full_symbol_names.append(i)


    return full_symbol_names

