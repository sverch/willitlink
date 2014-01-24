from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer
from willitlink.queries.fullnames import expand_file_names

def get_parent_objects(graph, build_object_name):
    """Gets the build objects that "include" the given build object

    A build object can "include" another build object in the following ways:

    1. Object included in archive
    2. Archive depended on by another archive
    3. Archive included in executable
    4. Header included in source file (currently the graph maps from header to object file)
    5. Source used to build object file

    Keyword Arguments:
    graph -- The MultiGraph that contains the dependency data about our build objects
    build_object_name -- The full name of the build object that we are looking for the parents of.
                         No name expansion is performed.
    """
    parents = []

    # Cases 1-3 - These are not currently distinguished in our graph object, and all share the same
    # relationship.
    archives_or_executables_including_or_containing = graph.get('dependency_to_targets', build_object_name)
    if archives_or_executables_including_or_containing is not None:
        parents.extend(archives_or_executables_including_or_containing)

    # Case 4 - Object files that include this header (the graph will return an empty list if this
    # build object is not a header)
    object_files_including = graph.get('header_to_files_including', build_object_name)
    if object_files_including is not None:
        parents.extend(object_files_including)

    # Case 5 - Object files that are built from this source (the graph will return an empty list if
    # this build object is not a source file)
    object_files_from_source = graph.get('source_to_file', build_object_name)
    if object_files_from_source is not None:
        parents.extend(object_files_from_source)

    return parents

def get_executable_list(graph, file_name):
    file_names = expand_file_names(graph, file_name)
    checked_file_names = set()

    # TODO: don't hard code these executable lists.  Instead, use something like this:
    # wil.py list files "" | grep -v "\."
    # This is getting the list of actual things that are built that have no file extension
    supported_binaries = [ "mongod", "mongos" ]
    tool_binaries = [ "mongotop", "mongodump", "mongoexport", "mongoimport", "mongobridge", "mongoperf", "bsondump", "mongofiles", "mongosniff", "mongorestore", "mongostat", "mongooplog" ]
    dbtests = [ "test", "perftest" ]
    client_examples = ["firstExample", "rsExample", "authTest", "httpClientTest", "tutorial", "clientTest", "whereExample", "secondExample" ]
    supported_binaries += tool_binaries
    supported_binaries += dbtests
    supported_binaries += client_examples

    result_binaries = set()
    for current_file_name in file_names:
        if current_file_name in supported_binaries:
            result_binaries.add(current_file_name)

        # Add the parents to the list we are iterating
        for parent in get_parent_objects(graph, current_file_name):
            if parent not in checked_file_names:
                file_names.append(parent)
                checked_file_names.add(parent)

    return list(result_binaries)
