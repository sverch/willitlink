from collections import OrderedDict
import sys


def underscore_name_to_title_name(name):
    return name.replace("_", " ").title()

def title_name_to_underscore_name(name):
    return name.lower().replace(" ", "_")

def is_new_schema(project_structure_data):
    return type(project_structure_data) is not dict

def old_schema_to_new_schema(project_structure_data):
    new_schema_project_structure_data = []

    for system_name in project_structure_data.keys():
        new_schema_system_object = OrderedDict()
        new_schema_system_object['system_title'] = underscore_name_to_title_name(system_name)
        new_schema_system_object['system_name'] = system_name
        new_schema_system_object['system_description'] = project_structure_data[system_name]['description']
        new_schema_system_object['system_modules'] = []
        for module_object in project_structure_data[system_name]['modules']:

            new_schema_module_object = OrderedDict()
            new_schema_module_object['module_title'] = underscore_name_to_title_name(module_object['name'])
            new_schema_module_object['module_name'] = module_object['name']
            new_schema_module_object['module_description'] = module_object['description']
            new_schema_module_object['module_groups'] = []
            for group_object in module_object['groups']:

                new_schema_group_object = OrderedDict()
                new_schema_group_object['group_title'] = group_object['name'] if 'name' in group_object else "TODO: Name this group"
                new_schema_group_object['group_description'] = group_object['comments']
                new_schema_group_object['group_files'] = group_object['files']

                new_schema_module_object['module_groups'].append(new_schema_group_object)

            new_schema_system_object['system_modules'].append(new_schema_module_object)

        new_schema_project_structure_data.append(new_schema_system_object)

    return new_schema_project_structure_data

def new_schema_to_old_schema(project_structure_data):
    old_schema_project_structure_data = {}

    for system_object in project_structure_data:
        old_schema_system_object = {}
        old_schema_system_object['description'] = system_object['system_description']
        old_schema_system_object['modules'] = []
        for module_object in system_object['system_modules']:

            old_schema_module_object = {}
            old_schema_module_object['name'] = module_object['module_name']
            old_schema_module_object['title'] = module_object['module_name']
            old_schema_module_object['description'] = module_object['module_description']
            old_schema_module_object['groups'] = []
            for group_object in module_object['module_groups']:

                old_schema_group_object = {}
                old_schema_group_object['comments'] = group_object['group_description']
                if group_object['group_title'] != "TODO: Name this group":
                    old_schema_group_object['name'] = group_object['group_title']
                old_schema_group_object['files'] = group_object['group_files']

                old_schema_module_object['groups'].append(old_schema_group_object)

            old_schema_system_object['modules'].append(old_schema_module_object)

        old_schema_project_structure_data[system_object['system_name']] = old_schema_system_object

    return old_schema_project_structure_data
