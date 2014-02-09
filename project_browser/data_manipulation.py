# The project has files in nested categories.  This returns a list of all files for the project.
def get_all_project_files(project_data):
    all_files = []
    for system_object in project_data:
        for module_object in system_object['system_modules']:
            for module_group in module_object['module_groups']:
                all_files.extend(module_group['group_files'])
    return all_files

# The modules have files listed in "groups".  This returns a list of all files for the module.
def flat_module_files(single_module_data):
    module_files = []
    for module_group in single_module_data['module_groups']:
        module_files.extend(module_group['group_files'])
    return module_files
