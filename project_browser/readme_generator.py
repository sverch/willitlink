import os
import yaml
import sys
from data_access import validate_project_structure_file_schema, read_project_structure_file, load_willitlink_graph
from get_willitlink_data import get_version_and_build_info, get_file_interface, get_file_headers, get_file_dependencies, get_file_executables


# Helpers to generate a tree of github browseable README.md files from our willitlink data and from
# our project data.



# Link into the MongoDB source tree on github
base_github_url = "https://github.com/mongodb/mongo/tree/"
def get_github_url(version_info, resource = ""):

    # Get the base link to the project tree
    full_github_url = base_github_url

    # For the actual version reference, first try tag
    if version_info['tag'] != "(no tag)":
        full_github_url = full_github_url + version_info['tag']
    # Then try branch
    elif version_info['branch'] != "(no branch)":
        full_github_url = full_github_url + version_info['branch']
    # Finally, fall back to the exact git hash
    else:
        full_github_url = full_github_url + version_info['hash']

    # Now, link to the actual resource
    full_github_url = full_github_url + "/" + resource

    return full_github_url

# The formating we have in the YAML file and the formatting that makes markdown display the
# description nicely are different
def cleanup_description_for_markdown(description):
    return description.replace("#", " ").replace("_", "\\_").replace("\n", "\n\n").lstrip()

# Outputs a top level README.md file for the project
def output_readme_files_for_project(graph, project_directory, project_data, file_to_system, file_to_module, version_and_build_info):
    project_readme = open(os.path.join(project_directory, "README.md"), 'w')
    project_readme.truncate()

    project_readme.write("# MongoDB Server Codebase Map\n")
    project_readme.write("Categorization and documentation of the MongoDB server codebase.  ")
    project_readme.write("This is a work in progress, and is by no means comprehensive.  ")
    project_readme.write("Feel free to submit pull requests or suggestions.\n\n")
    project_readme.write("NOTE:  This README and entire subtree is automatically generated.\n\n")

    project_readme.write("* Build flags: " + ' '.join(version_and_build_info['build_info']['flags']) + "\n")
    project_readme.write("* Build platform: " + version_and_build_info['build_info']['platform'] + "\n")
    project_readme.write("* Version hash: " + version_and_build_info['version_info']['hash'] + "\n")
    project_readme.write("* Version branch: " + version_and_build_info['version_info']['branch'] + "\n")
    project_readme.write("* Version tag: " + version_and_build_info['version_info']['tag'] + "\n")
    project_readme.write("* Github URL: " + get_github_url(version_and_build_info['version_info']) + "\n\n")

    for system_object in project_data:

        # Sanitize the system name for this sytem readme link
        markdown_sanitized_system_name = system_object['system_name'].replace("_", "\\_")

        # Header for this system with link
        project_readme.write("## [" + system_object['system_title'] + "](" + markdown_sanitized_system_name + ")" + "\n")

        # Output the description for this system
        project_readme.write(cleanup_description_for_markdown(system_object["system_description"]) + "\n\n")

        # Actually output the readme for the system itself and all modules
        output_readme_files_for_system(graph, project_directory, file_to_system, file_to_module, version_and_build_info['version_info'], system_object)



# Outputs a README.md file for each system with some useful information
def output_readme_files_for_system(graph, project_directory, file_to_system, file_to_module, version_info, system_object):
    system_directory = os.path.join(project_directory, system_object['system_name'])
    if not os.path.exists(system_directory):
        os.mkdir(system_directory)

    system_readme = open(os.path.join(system_directory, "README.md"), 'w')
    system_readme.truncate()

    # Add the header for this system
    system_readme.write("# " + system_object["system_title"] + "\n\n")

    # Output the description for this system
    system_readme.write(cleanup_description_for_markdown(system_object["system_description"]) + "\n\n")

    # Output module information for this system
    system_readme.write("## Modules\n\n")
    for module_object in system_object['system_modules']:

        # Sanitize the module name for this sytem readme
        markdown_sanitized_module_name = module_object['module_name'].replace("_", "\\_")

        # Information for this module
        system_readme.write("### [" + module_object['module_title'] + "](" + markdown_sanitized_module_name + ")" + "\n")
        system_readme.write(cleanup_description_for_markdown(module_object["module_description"]) + "\n\n")

        output_readme_files_for_module(graph, system_directory, version_info, file_to_module, file_to_system, module_object)



# The modules have files listed in "groups".  This returns a list of all files for the module.
def flat_module_files(single_module_data):
    module_files = []
    for module_group in single_module_data['module_groups']:
        module_files.extend(module_group['group_files'])
    return module_files

# Builds a map of source files to system names
def build_file_to_system_map(project_data):
    file_to_system = {}
    for system_object in project_data:
        for module_object in system_object['system_modules']:
            for module_file in flat_module_files(module_object):
                file_to_system[module_file] = system_object['system_name']
    return file_to_system

# Builds a map of source files to module names
def build_file_to_module_map(project_data):
    file_to_module = {}
    for system_object in project_data:
        for module_object in system_object['system_modules']:
            for module_file in flat_module_files(module_object):
                file_to_module[module_file] = module_object['module_name']
    return file_to_module

def filter_own_module_interface(file_interface, module_name, file_to_module):
    new_interface_objects = []
    for interface_object in file_interface:
        new_symbol_sources = []
        new_interface_object = {}
        for use_file in interface_object['symbol_uses']:
            if file_to_module[use_file] != module_name:
                new_symbol_sources.append(use_file)

        if len(new_symbol_sources) > 0:
            new_interface_object['symbol_name'] = interface_object['symbol_name']
            new_interface_object['symbol_uses'] = new_symbol_sources
            new_interface_objects.append(new_interface_object)

    return new_interface_objects

def filter_own_module_dependencies(file_dependencies, module_name, file_to_module):
    new_dependency_objects = []
    for dependency_object in file_dependencies:
        new_symbol_sources = []
        new_dependency_object = {}
        for source_file in dependency_object['symbol_sources']:
            if file_to_module[source_file] != module_name:
                new_symbol_sources.append(source_file)

        if len(new_symbol_sources) > 0:
            new_dependency_object['symbol_name'] = dependency_object['symbol_name']
            new_dependency_object['symbol_sources'] = new_symbol_sources
            new_dependency_objects.append(new_dependency_object)

    return new_dependency_objects

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

def output_readme_file_for_group_interface(graph, group_interface_file, module_group, module_object, file_to_module, file_to_system):

    # Write out the interface README
    group_interface_file.write("\n# Interface for " + module_group["group_title"] + "\n")
    group_interface_file.write("This interface information represents symbols that "
        "are defined in this group but used in other modules.  Does not include "
        "symbols defined in this group that are used inside this module.\n")
    something_in_interface = False
    # Iterate over all the files in this group
    for file_name in module_group['group_files']:

        # Get interface for this file
        file_interface = get_file_interface(graph, file_name)

        # Filter out file interface objects that don't have any edges to outside this module
        file_interface = filter_own_module_interface(file_interface, module_object['module_name'], file_to_module)

        if len(file_interface) > 0:
            something_in_interface = True
            group_interface_file.write("\n### " + file_name.replace("_", "\\_") + "\n")
            for interface_object in file_interface:
                group_interface_file.write("\n<div></div>\n") # This is a weird markdown idiosyncrasy to
                                        # make sure the indented block with the symbol
                                        # is interpreted as a literal block
                group_interface_file.write("\n    " + interface_object['symbol_name'] + "\n\n")
                group_interface_file.write("- Used By:\n\n")
                for file_using in interface_object['symbol_uses']:
                    if file_using in file_to_module:
                        group_interface_file.write("    - [" + file_using.replace("_", "\\_") + "](../../../../" + file_to_system[file_using].replace("_", "\\_") + "/" + file_to_module[file_using].replace("_", "\\_") + ")" + "\n")
                    else:
                        group_interface_file.write("    - " + file_using.replace("_", "\\_") + "\n")
    if not something_in_interface:
        group_interface_file.write("(not used outside this module)\n")

def output_readme_file_for_group_dependencies(graph, group_dependencies_file, module_group, module_object, file_to_module, file_to_system):

    # Write out the dependencies README
    group_dependencies_file.write("\n# Dependencies for " + module_group["group_title"] + "\n")
    group_dependencies_file.write("This dependency information represents symbols "
        "that are used in this group but defined in other modules.  Does not include "
        "symbols used in this group that are defined inside this module.\n")
    something_in_dependencies = False
    # Iterate over all the files in this group
    for file_name in module_group['group_files']:

        # Get dependencies for this file
        file_dependencies = get_file_dependencies(graph, file_name)

        # Filter out file dependency objects that don't have any edges to outside this module
        file_dependencies = filter_own_module_dependencies(file_dependencies, module_object['module_name'], file_to_module)

        if len(file_dependencies) > 0:
            something_in_dependencies = True
            group_dependencies_file.write("\n### " + file_name.replace("_", "\\_") + "\n")
            for dependencies_object in file_dependencies:
                group_dependencies_file.write("\n<div></div>\n") # This is a weird markdown idiosyncrasy to
                                        # make sure the indented block with the symbol
                                        # is interpreted as a literal block
                group_dependencies_file.write("\n    " + dependencies_object['symbol_name'] + "\n\n")
                group_dependencies_file.write("- Provided By:\n\n")
                for file_providing in dependencies_object['symbol_sources']:
                    if file_providing in file_to_module:
                        group_dependencies_file.write("    - [" + file_providing.replace("_", "\\_") + "](../../../../" + file_to_system[file_providing].replace("_", "\\_") + "/" + file_to_module[file_providing].replace("_", "\\_") + ")" + "\n")
                    else:
                        group_dependencies_file.write("    - " + file_providing.replace("_", "\\_") + "\n")
    if not something_in_dependencies:
        group_dependencies_file.write("(no dependencies outside this module)\n")

def output_readme_files_for_module(graph, system_directory, version_info, file_to_module, file_to_system, module_object):

        module_directory = os.path.join(system_directory, module_object['module_name'])
        if not os.path.exists(module_directory):
            os.mkdir(module_directory)

        module_readme = open(os.path.join(module_directory, "README.md"), 'w')
        module_readme.truncate()

        # First, the and descriptiontitle of the module
        module_readme.write("# " + module_object['module_title'] + "\n")
        module_readme.write(cleanup_description_for_markdown(module_object["module_description"]) + "\n\n")

        group_number = 0

        # Create directories for automatically generated information
        interface_dir = os.path.join(module_directory, "interface")
        if not os.path.exists(interface_dir):
            os.mkdir(interface_dir)
        dependencies_dir = os.path.join(module_directory, "dependencies")
        if not os.path.exists(dependencies_dir):
            os.mkdir(dependencies_dir)

        # Do the following analysis for each group separately
        for module_group in module_object['module_groups']:

            # Horizontal rule
            module_readme.write("\n-------------\n\n")

            # Comments for this group of files
            module_readme.write("## " + module_group["group_title"] + "\n")
            module_readme.write(cleanup_description_for_markdown(module_group["group_description"]) + "\n\n")

            # Files in this module group
            module_readme.write("#### Files\n")
            for file_name in module_group['group_files']:

                # Actual displayed file name
                module_readme.write("- [" + file_name.replace("_", "\\_") + "]")

                # Link to github project
                module_readme.write("(" + get_github_url(version_info, file_name) + ")")

                # List of executables file is built into
                module_readme.write("   (" + ", ".join(get_exec_digest(get_file_executables(graph, file_name))) + ")\n")

            # Interface for this module group (symbols used from outside this module)
            # Make sure the "group interface" directory exists
            # NOTE: Since not all groups have a name, we have no choice but to just number
            # the groups.
            group_interface_dir = os.path.join(interface_dir, str(group_number))
            if not os.path.exists(group_interface_dir):
                os.mkdir(group_interface_dir)

            group_interface_file = open(os.path.join(group_interface_dir, "README.md"), "w")

            # Link to the group directory which will have the interface README
            module_readme.write("\n#### [Interface](" + "interface/" + str(group_number) + ")\n")

            # Actually emit the README.md file for the interface
            output_readme_file_for_group_interface(graph, group_interface_file, module_group, module_object, file_to_module, file_to_system)

            # Dependencies for this module group (symbols used that are defined outside this module)
            # Make sure the "group dependencies" directory exists
            # NOTE: Since not all groups have a name, we have no choice but to just number
            # the groups.
            group_dependencies_dir = os.path.join(dependencies_dir, str(group_number))
            if not os.path.exists(group_dependencies_dir):
                os.mkdir(group_dependencies_dir)

            group_dependencies_file = open(os.path.join(group_dependencies_dir, "README.md"), "w")

            # Link to the group directory which will have the dependencies README
            module_readme.write("\n#### [Dependencies](" + "dependencies/" + str(group_number) + ")\n")

            # Actually emit the README.md file for the dependencies
            output_readme_file_for_group_dependencies(graph, group_dependencies_file, module_group, module_object, file_to_module, file_to_system)

            group_number = group_number + 1

def generate_readme_tree(graph, dest_directory, project_data, version_and_build_info):

    if not os.path.exists(dest_directory):
        os.mkdir(dest_directory)

    # TODO: Handle this in a better way.  Perhaps just make it part of "project_data" or make a
    # ProjectData object.
    file_to_system = build_file_to_system_map(project_data)
    file_to_module = build_file_to_module_map(project_data)

    output_readme_files_for_project(graph, dest_directory, project_data, file_to_system, file_to_module, version_and_build_info)

def main():

    if len(sys.argv) != 3:
        print "Usage: <base_data_directory> <dest_directory>"
        exit(1)

    base_data_directory = sys.argv[1]
    dest_directory = sys.argv[2]

    print("Validating schema of human generated project data file...")
    validate_project_structure_file_schema(base_data_directory)

    print("Loading willitlink data...")
    graph = load_willitlink_graph(base_data_directory)

    print("Reading the processed project data file with willitlink data...")
    project_data = read_project_structure_file(base_data_directory)

    print("Getting version and build info from willitlink data...")
    version_and_build_info = get_version_and_build_info(graph)

    print("Generating README tree...")
    generate_readme_tree(graph, dest_directory, project_data, version_and_build_info)

if __name__ == '__main__':
    main()
