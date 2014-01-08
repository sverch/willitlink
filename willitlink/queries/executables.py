from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer
from willitlink.queries.symbol_diff import get_full_filenames

def get_executable_list(g, file_name):
    file_names = get_full_filenames(g, file_name)
    checked_file_names = set()
    supported_binaries = [ "mongod", "mongos" ]
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
