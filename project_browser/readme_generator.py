import os
import yaml
import sys
from process_project_data import generate_willitlink_data, get_processed_project_data
from data_manipulation import flat_module_files
from data_access import validate_project_structure_file_schema


# Helpers to generate a tree of github browseable README.md files from our willitlink data and from
# our project data.


# Outputs a README.md file for each system with some useful information
def output_readme_files_for_systems(project_directory, project_data):
    for system_object in project_data:
        system_directory = os.path.join(project_directory, system_object['system_name'])

        top_level_readme = open(os.path.join(system_directory, "README.md"), 'w')
        top_level_readme.truncate()

        # Add the header for this system
        markdown_sanitized_system_object = system_object["system_title"]
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
                for source_file in flat_module_files(module_object):
                    markdown_sanitized_source_file = source_file.replace("_", "\\_")
                    top_level_readme.write("- [" + markdown_sanitized_source_file + "](" + markdown_sanitized_module_name + ")" + "\n")



# Builds a map of source files to modules
def build_file_to_module_map(project_data):
    file_to_module = {}
    for system_object in project_data:
        for module_object in system_object['system_modules']:
            for module_file in flat_module_files(module_object):
                file_to_module[module_file] = module_object['module_name']
    return file_to_module

def filter_own_module_interface(project_data, file_objects, self_name):
    file_to_module = build_file_to_module_map(project_data)
    result_file_objects = []
    for file_object in file_objects:
        new_interface_objects = []
        for interface_object in file_object['file_interface']:
            new_symbol_sources = []
            new_interface_object = {}
            for use_file in interface_object['symbol_uses']:
                if file_to_module[use_file] != self_name:
                    new_symbol_sources.append(use_file)

            if len(new_symbol_sources) > 0:
                new_interface_object['symbol_name'] = interface_object['symbol_name']
                new_interface_object['symbol_uses'] = new_symbol_sources
                new_interface_objects.append(new_interface_object)

        if len(new_interface_objects) > 0:
            file_object['file_interface'] = new_interface_objects
            result_file_objects.append(file_object)

    return result_file_objects

def filter_own_module_dependencies(project_data, file_objects, self_name):
    file_to_module = build_file_to_module_map(project_data)
    result_file_objects = []
    for file_object in file_objects:
        new_dependency_objects = []
        for dependency_object in file_object['file_dependencies']:
            new_symbol_sources = []
            new_dependency_object = {}
            for source_file in dependency_object['symbol_sources']:
                if file_to_module[source_file] != self_name:
                    new_symbol_sources.append(source_file)

            if len(new_symbol_sources) > 0:
                new_dependency_object['symbol_name'] = dependency_object['symbol_name']
                new_dependency_object['symbol_sources'] = new_symbol_sources
                new_dependency_objects.append(new_dependency_object)

        if len(new_dependency_objects) > 0:
            file_object['file_dependencies'] = new_dependency_objects
            result_file_objects.append(file_object)

    return result_file_objects

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
    file_to_module = build_file_to_module_map(project_data)

    for system_object in project_data:
        modules_directory = os.path.join(project_directory, system_object['system_name'])

        for module_object in system_object['system_modules']:
            module_path = os.path.join(modules_directory, module_object['module_name'])
            if os.path.isdir(module_path):

                module_readme = open(os.path.join(module_path, "README.md"), 'w')
                module_readme.truncate()
                # First, the title of the module
                module_readme.write("# " + module_object['module_title'] + "\n\n")

                module_readme.write("# Module Groups\n")

                group_number = 0

                # Do the following analysis for each group separately
                for module_group in module_object['module_groups']:

                    # Horizontal rule
                    module_readme.write("\n-------------\n\n")

                    # Comments for this group of files
                    module_readme.write("# " + module_group["group_title"] + "\n")
                    module_readme.write(module_group["group_description"].replace("#", " ").replace("_", "\\_").lstrip() + "\n\n")

                    # Files in this module group
                    module_readme.write("## Files\n")
                    for file_object in module_group["group_generated_data"]:
                        module_readme.write("- " + file_object['file_name'].replace("_", "\\_"))
                        module_readme.write("   (" + ", ".join(get_exec_digest(file_object['file_executables'])) + ")\n")

                    # Interface for this module group (symbols used from outside this module)
                    # 1.  Make sure the "interface" directory exists
                    interface_dir = os.path.join(module_path, "interface")
                    if not os.path.exists(interface_dir):
                        os.mkdir(interface_dir)

                    # 2.  Make sure the "group interface" directory exists
                    # NOTE: Since not all groups have a name, we have no choice but to just number
                    # the groups.
                    group_interface_dir = os.path.join(interface_dir, str(group_number))
                    if not os.path.exists(group_interface_dir):
                        os.mkdir(group_interface_dir)

                    group_interface_file = open(os.path.join(group_interface_dir, "README.md"), "w")

                    # 3.  Link to the group directory which will have the interface README
                    module_readme.write("\n#### [Interface](" + os.path.join("interface", str(group_number)) + ")\n")

                    # 4.  Write out the interface README
                    group_interface_file.write("\n# Interface\n")
                    something_in_interface = False
                    file_interface_external = filter_own_module_interface(project_data, module_group["group_generated_data"], module_object['module_name'])
                    for file_object in file_interface_external:
                        if len(file_object['file_interface']) > 0:
                            something_in_interface = True
                            group_interface_file.write("\n### " + file_object['file_name'].replace("_", "\\_") + "\n")
                            for interface_object in file_object['file_interface']:
                                group_interface_file.write("\n<div></div>\n") # This is a weird markdown idiosyncrasy to
                                                        # make sure the indented block with the symbol
                                                        # is interpreted as a literal block
                                group_interface_file.write("\n    " + interface_object['symbol_name'] + "\n\n")
                                group_interface_file.write("- Used By:\n\n")
                                for file_using in interface_object['symbol_uses']:
                                    if file_using in file_to_module:
                                        group_interface_file.write("    - [" + file_using.replace("_", "\\_") + "](../../../" + file_to_module[file_using].replace("_", "\\_") + ")" + "\n")
                                    else:
                                        group_interface_file.write("    - " + file_using.replace("_", "\\_") + "\n")
                    if not something_in_interface:
                        group_interface_file.write("(not used outside this module)\n")

                    # Dependencies for this module group (symbols used that are defined outside this module)
                    # 1.  Make sure the "dependencies" directory exists
                    dependencies_dir = os.path.join(module_path, "dependencies")
                    if not os.path.exists(dependencies_dir):
                        os.mkdir(dependencies_dir)

                    # 2.  Make sure the "group dependencies" directory exists
                    # NOTE: Since not all groups have a name, we have no choice but to just number
                    # the groups.
                    group_dependencies_dir = os.path.join(dependencies_dir, str(group_number))
                    if not os.path.exists(group_dependencies_dir):
                        os.mkdir(group_dependencies_dir)

                    group_dependencies_file = open(os.path.join(group_dependencies_dir, "README.md"), "w")

                    # 3.  Link to the group directory which will have the dependencies README
                    module_readme.write("\n#### [Dependencies](" + os.path.join("dependencies", str(group_number)) + ")\n")

                    group_dependencies_file.write("\n# Dependencies\n")
                    something_in_dependencies = False
                    file_dependencies_external = filter_own_module_dependencies(project_data, module_group["group_generated_data"], module_object['module_name'])
                    for file_object in file_dependencies_external:
                        if len(file_object['file_dependencies']) > 0:
                            something_in_dependencies = True
                            group_dependencies_file.write("\n### " + file_object['file_name'].replace("_", "\\_") + "\n")
                            for dependencies_object in file_object['file_dependencies']:
                                group_dependencies_file.write("\n<div></div>\n") # This is a weird markdown idiosyncrasy to
                                                        # make sure the indented block with the symbol
                                                        # is interpreted as a literal block
                                group_dependencies_file.write("\n    " + dependencies_object['symbol_name'] + "\n\n")
                                group_dependencies_file.write("- Provided By:\n\n")
                                for file_providing in dependencies_object['symbol_sources']:
                                    if file_providing in file_to_module:
                                        group_dependencies_file.write("    - [" + file_providing.replace("_", "\\_") + "](../../../" + file_to_module[file_providing].replace("_", "\\_") + ")" + "\n")
                                    else:
                                        group_dependencies_file.write("    - " + file_providing.replace("_", "\\_") + "\n")
                    if not something_in_dependencies:
                        group_dependencies_file.write("(no dependencies outside this module)\n")

                    group_number = group_number + 1

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

    if not os.path.exists(dest_directory):
        os.mkdir(dest_directory)

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

    print("Validating schema of human generated project data file...")
    validate_project_structure_file_schema(base_data_directory)

    print("Merging in the willitlink data...")
    generate_willitlink_data(base_data_directory)

    print("Reading the processed project data file with willitlink data...")
    project_data = get_processed_project_data(base_data_directory)

    print("Generating README tree...")
    generate_readme_tree(dest_directory, project_data)

if __name__ == '__main__':
    main()
