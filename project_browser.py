import sys
import json

from project_browser.process_project_data import generate_willitlink_data, get_processed_project_data

# API example for merging project data with willitlink and getting access to the result
#
# Note: to use this, the base_directory must have the following:
# modules.yaml - human generated project data file
# willitlink-data - willitlink data directory (must be built against same version)

def main():

    if len(sys.argv) != 2:
        print "Usage: <base_directory>"
        exit(1)

    base_directory = sys.argv[1]

    # Merge in the willitlink data
    generate_willitlink_data(base_directory)

    # Get and print the merged data
    print json.dumps(get_processed_project_data(base_directory))

if __name__ == '__main__':
    main()

