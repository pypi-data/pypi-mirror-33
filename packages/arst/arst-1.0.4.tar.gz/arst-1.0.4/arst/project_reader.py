from typing import List
import mdvl
import sys
import os.path
import yaml

from .color_functions import red
from .file_resolver import FileResolver


class ProjectDefinition(object):
    name: str
    projects_folder: str
    search_path: List[str]
    generate_ars: bool

    def __init__(self,
                 projects_folder: str,
                 name: str,
                 generate_ars: bool=True) -> None:
        self.name = name
        self.projects_folder = projects_folder
        self.search_path = [name]
        self.generate_ars = generate_ars

    def file_resolver(self) -> FileResolver:
        return FileResolver(root_projects_folder=self.projects_folder,
                            search_path=self.search_path)


def read_project_definition(projects_folder: str,
                            project_name: str) -> ProjectDefinition:
    full_project_path = os.path.join(projects_folder, project_name)

    # Simple sanity check to see if there is a project there, instead
    # of reporting an error.
    if not os.path.isdir(full_project_path):
        print(red("Folder"),
              red(f"'{full_project_path}'", bold=True),
              red("does not exist, or is not a folder."))
        sys.exit(1)

    help_file_name = os.path.join(projects_folder, project_name, "HELP.md")
    if os.path.isfile(help_file_name):
        with open(help_file_name, encoding='utf-8') as help_file:
            mdvl.render(help_file.read(), cols=80)

    result = ProjectDefinition(name=project_name,
                               projects_folder=projects_folder)

    template_settings_path = os.path.join(full_project_path, '.ars')

    if not os.path.isfile(template_settings_path):
        return result

    with open(template_settings_path, encoding='utf-8') as template_settings_content:
        settings = yaml.load(template_settings_content.read())

    if "noars" in settings and settings["noars"]:
        result.generate_ars = False

    if "parents" in settings:
        for parent in settings["parents"]:
            parent_project = read_project_definition(projects_folder, parent)
            result.search_path.extend(parent_project.search_path)

    return result
