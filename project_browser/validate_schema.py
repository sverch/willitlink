from data_access import read_project_structure_file, validate_project_structure_file_schema
import sys

def main():

    if len(sys.argv) != 2:
        print "Usage: <base_directory>"
        exit(1)

    base_directory = sys.argv[1]

    validate_project_structure_file_schema(base_directory)

    print("Schema validated successfully!")

if __name__ == '__main__':
    main()

