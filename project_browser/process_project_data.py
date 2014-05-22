import sys

from get_willitlink_data import add_willitlink_data
from data_access import read_project_structure_file, load_willitlink_graph, write_processed_project_structure_file, read_processed_project_structure_file

# This is the first interface to the willitlink doc data generator
# Note: This depends on willitlink-data being in the base directory and containing willitlink data


# This takes the human generated module file and merges it with the willitlink data
# base_directory must contain:
#
# modules.yaml - human generated project data file
# willitlink-data - willitlink data directory
#
# This will dump a modules_processed.yaml file in the base_directory
def generate_willitlink_data(base_directory):
    # Read the project data
    project_data = read_project_structure_file(base_directory)

    # Add the data from willitlink
    graph = load_willitlink_graph(base_directory)
    add_willitlink_data(graph, project_data)

    # Dump the processed project data
    write_processed_project_structure_file(base_directory, project_data)

# This gets the merged module file (modules_processed.yaml) and returns it as a python dict
def get_processed_project_data(base_directory):
    return read_processed_project_structure_file(base_directory)

def get_version_and_build_info(base_directory):
    # Get version and build info from willitlink
    graph = load_willitlink_graph(base_directory)
    return graph.get_extra_info()

def main():

    if len(sys.argv) != 2:
        print "Usage: <base_directory>"
        exit(1)

    base_directory = sys.argv[1]

    # Read the project data
    project_data = read_project_structure_file(base_directory)

    # Add the data from willitlink
    graph = load_willitlink_graph(base_directory)
    add_willitlink_data(graph, project_data)

    # Dump the processed project data
    write_processed_project_structure_file(base_directory, project_data)

if __name__ == '__main__':
    main()

