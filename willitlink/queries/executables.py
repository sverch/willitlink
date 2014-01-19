from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer
from willitlink.queries.fullnames import get_full_filenames

def get_executable_list(g, file_name):
    file_names = get_full_filenames(g, file_name)
    checked_file_names = set()

    # TODO: don't hard code this list.  Instead, use something like this:
    # wil.py list files "" | grep -v \.cpp\" | grep -v \.o\" | grep -v \.a\" | grep -v \.c\" | grep
    # -v \.h\" | grep -v \.hpp\" |grep -v \.cc\" | grep -v \.js\" | grep -v \.txt\" | grep -v
    # \.dylib\" | grep "build\/darwin"
    # This is getting the list of actual things that are built that have no file extension (I know
    # there was a less dumb way to write that shell statement, but that was the easiest at the time)
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
        for parent in g.get('dependency_to_targets', current_file_name):
            if parent not in checked_file_names:
                file_names.append(parent)
                checked_file_names.add(parent)

    return list(result_binaries)
