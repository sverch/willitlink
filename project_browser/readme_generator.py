import os
import yaml
import sys
from process_project_data import generate_willitlink_data, get_processed_project_data


# Helpers to generate a tree of github browseable README.md files from our willitlink data and from
# our project data.


# Outputs a README.md file for each system with some useful information
def output_readme_files_for_systems(project_directory, project_data):
    for system_object in project_data:
        system_directory = os.path.join(project_directory, system_object['system_name'])

        top_level_readme = open(os.path.join(system_directory, "README.md"), 'w')
        top_level_readme.truncate()

        # Add the header for this system
        markdown_sanitized_system_object = system_object["system_name"].replace("_", "\\_")
        top_level_readme.write("# " + markdown_sanitized_system_object + "\n\n")

        # TODO: add the description for this system

        # Output module information for this system
        top_level_readme.write("## Modules\n\n")
        for module_object in system_object['system_modules']:
            module_path = os.path.join(system_directory, module_object['module_name'])
            if os.path.isdir(module_path):

                # Sanitize the module name for this sytem readme
                markdown_sanitized_module_name = module_object['module_name'].replace("_", "\\_")

                # Heading for this module
                top_level_readme.write("### " + markdown_sanitized_module_name + "\n\n")

                # Files in this module
                for source_file in module_object['files_flat']:
                    markdown_sanitized_source_file = source_file.replace("_", "\\_")
                    top_level_readme.write("- [" + markdown_sanitized_source_file + "](" + markdown_sanitized_module_name + ")" + "\n")



# Builds a map of source files to modules
def build_file_to_module_map(project_data):
    file_to_module = {}
    for system_object in project_data:
        for module_object in system_object['system_modules']:
            for module_file in module_object['files_flat']:
                file_to_module[module_file] = module_object['module_name']
    return file_to_module

# Builds a map of source files to executables
def build_file_to_executables_map(project_data):
    file_to_executables = {}
    for system_object in project_data:
        for module_object in system_object['system_modules']:
            for file_with_exec in module_object['files_with_exec']:
                if (file_with_exec["name"] is not None):
                    file_to_executables[file_with_exec['name']] = file_with_exec['execs']
    return file_to_executables

# Builds a map of source files to interface
def build_file_to_interface_map(project_data):
    file_to_interface = {}
    for system_object in project_data:
        for module_object in system_object['system_modules']:
            for interface_object in module_object['interface']:
                file_name = interface_object['object']
                if file_name not in file_to_interface:
                    file_to_interface[file_name] = []
                file_to_interface[file_name].append(interface_object)
    return file_to_interface

# Builds a map of source files to dependencies
def build_file_to_dependencies_map(project_data):
    file_to_dependencies = {}
    for system_object in project_data:
        for module_object in system_object['system_modules']:
            for dependencies_object in module_object['leaks']:
                file_name = dependencies_object['object']
                if file_name not in file_to_dependencies:
                    file_to_dependencies[file_name] = []
                file_to_dependencies[file_name].append(dependencies_object)
    return file_to_dependencies

# Simplifies the list of executables into something more readable.
#
# Example:
# [ "mongod", "mongos", "mongotop", "mongodump", "mongoexport", "mongoimport", "mongobridge",
# "mongoperf", "bsondump", "mongofiles", "mongosniff", "mongorestore", "mongostat", "mongooplog" ]
#
# Turns into:
#
# [ "mongod", "mongos", "tools" ]
def get_exec_digest(exec_list):
    supported_binaries = [ "mongod", "mongos" ]
    tool_binaries = [ "mongotop", "mongodump", "mongoexport", "mongoimport", "mongobridge",
            "mongoperf", "bsondump", "mongofiles", "mongosniff", "mongorestore", "mongostat",
            "mongooplog" ]
    dbtests = [ "test", "perftest" ]
    client_examples = ["firstExample", "rsExample", "authTest", "httpClientTest", "tutorial", "clientTest", "whereExample", "secondExample" ]

    exec_digest = set()
    for exec_name in exec_list:
        if exec_name in supported_binaries:
            exec_digest.add(exec_name)
        if exec_name in tool_binaries:
            exec_digest.add("tools")
        if exec_name in client_examples:
            exec_digest.add("cppclientdriver")
        # Do nothing if exec_name in dbtests

    return list(exec_digest)

# Outputs a README.md file for each module with some useful information
def output_readme_files_for_modules(project_directory, project_data):
    file_to_executables = build_file_to_executables_map(project_data)
    file_to_interface = build_file_to_interface_map(project_data)
    file_to_dependencies = build_file_to_dependencies_map(project_data)
    file_to_module = build_file_to_module_map(project_data)

    for system_object in project_data:
        modules_directory = os.path.join(project_directory, system_object['system_name'])

        for module_object in system_object['system_modules']:
            module_path = os.path.join(modules_directory, module_object['module_name'])
            if os.path.isdir(module_path):

                f = open(os.path.join(module_path, "README.md"), 'w')
                f.truncate()
                # First, the title of the module
                f.write("# " + module_object['module_name'].replace("_", "\\_") + "\n\n")

                f.write("# Module Groups\n")

                # Do the following analysis for each group separately
                for module_group in module_object['module_groups']:

                    # Horizontal rule
                    f.write("\n-------------\n\n")

                    # Comments for this group of files
                    f.write("# Group Description\n")
                    f.write(module_group["group_description"].replace("#", " ").replace("_", "\\_").lstrip() + "\n\n")

                    # Files in this module group
                    f.write("# Files\n")
                    for file_name in module_group["group_files"]:
                        f.write("- " + file_name.replace("_", "\\_"))
                        if file_name in file_to_executables:
                            file_to_executables[file_name]
                            f.write("   (" + ", ".join(get_exec_digest(file_to_executables[file_name])) + ")\n")
                        else:
                            f.write("\n")

                    # Interface for this module group (symbols used from outside this module)
                    f.write("\n# Interface\n")
                    something_in_interface = False
                    for file_name in module_group["group_files"]:
                        if file_name in file_to_interface:
                            something_in_interface = True
                            f.write("\n### " + file_name.replace("_", "\\_") + "\n")
                            for interface_object in file_to_interface[file_name]:
                                f.write("\n<div></div>\n") # This is a weird markdown idiosyncrasy to
                                                        # make sure the indented block with the symbol
                                                        # is interpreted as a literal block
                                f.write("\n    " + interface_object['symbol'] + "\n\n")
                                f.write("- Used By:\n\n")
                                for file_using in interface_object['used_by']:
                                    if file_using in file_to_module:
                                        f.write("    - [" + file_using.replace("_", "\\_") + "](../" + file_to_module[file_using].replace("_", "\\_") + ")" + "\n")
                                    else:
                                        f.write("    - " + file_using.replace("_", "\\_") + "\n")
                    if not something_in_interface:
                        f.write("(not used outside this module)\n")

                    # Dependencies for this module group (symbols used that are defined outside this module)
                    f.write("\n# Dependencies\n")
                    something_in_dependencies = False
                    for file_name in module_group["group_files"]:
                        if file_name in file_to_dependencies:
                            something_in_dependencies = True
                            f.write("\n### " + file_name.replace("_", "\\_") + "\n")
                            for dependencies_object in file_to_dependencies[file_name]:
                                f.write("\n<div></div>\n") # This is a weird markdown idiosyncrasy to
                                                        # make sure the indented block with the symbol
                                                        # is interpreted as a literal block
                                f.write("\n    " + dependencies_object['symbol'] + "\n\n")
                                f.write("- Provided By:\n\n")
                                for file_providing in dependencies_object['sources']:
                                    if file_providing in file_to_module:
                                        f.write("    - [" + file_providing.replace("_", "\\_") + "](../" + file_to_module[file_providing].replace("_", "\\_") + ")" + "\n")
                                    else:
                                        f.write("    - " + file_providing.replace("_", "\\_") + "\n")
                    if not something_in_dependencies:
                        f.write("(no dependencies outside this module)\n")



def dump_module_files(project_directory, project_data):

    for system_object in project_data:
        system_directory = os.path.join(project_directory, system_object['system_name'])
        if not os.path.exists(system_directory):
            os.mkdir(system_directory)
        for module_object in system_object['system_modules']:
            module_directory = os.path.join(system_directory, module_object['module_name'])
            if not os.path.exists(module_directory):
                os.mkdir(module_directory)
            module_file = open(os.path.join(module_directory, 'module.yaml'), 'w')
            module_file.write(yaml.dump(module_object, indent=4, default_flow_style=False))

    return project_data


def generate_readme_tree(dest_directory, project_data):

    # This code is all to dump the janky README files
    dump_module_files(dest_directory, project_data)
    output_readme_files_for_systems(dest_directory, project_data)
    output_readme_files_for_modules(dest_directory, project_data)

def main():

    if len(sys.argv) != 3:
        print "Usage: <base_data_directory> <dest_directory>"
        exit(1)

    base_data_directory = sys.argv[1]
    dest_directory = sys.argv[2]

    # Merge in the willitlink data
    generate_willitlink_data(base_data_directory)

    # Get and print the merged data
    project_data = get_processed_project_data(base_data_directory)

    # This code is all to dump the janky README files
    generate_readme_tree(dest_directory, project_data)

if __name__ == '__main__':
    main()
