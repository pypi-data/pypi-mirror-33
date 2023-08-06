import filecmp
import json
import os
import shutil
import sys
import pybars
from termcolor import colored, cprint
from shutil import copyfile
import subprocess
import re
from typing import Dict


ARS_PROJECTS_FOLDER: str = os.environ["ARS_PROJECTS_FOLDER"]\
    if "ARS_PROJECTS_FOLDER" in os.environ\
    else os.path.join(os.environ["HOME"], ".projects")

ARS_DIFF_TOOL: str = os.environ["ARS_DIFF_TOOL"]\
    if "ARS_DIFF_TOOL" in os.environ\
    else os.path.join("vimdiff")


PARAM_RE = re.compile("^(.*?)(=(.*))?$")


class ParsedFile(object):
    name: str
    original_name: str
    keep_existing: bool
    hbs_template: bool

    def __init__(self, original_name: str) -> None:
        self.name = None
        self.original_name = original_name
        self.keep_existing = False
        self.hbs_template = False


def parse_file_name(file_name: str, project_parameters: Dict[str, str]) -> ParsedFile:
    """
    parseFileName - Parse the fie name
    :param file_name: string with filename
    :return: result dict
    """
    result = ParsedFile(file_name)

    name: str = file_name

    if name.endswith('.KEEP'):
        result.keep_existing = True
        name = name[0: -len(".KEEP")]

    if name.endswith(".hbs"):
        result.hbs_template = True
        name = name[0: -len(".hbs")]

    result.name = pybars.Compiler().compile(name)(project_parameters)

    return result


def execute_diff(file1: str, file2: str):
    subprocess.call([ARS_DIFF_TOOL, file1, file2])


class Main:
    def __init__(self):
        self.generate_ars = True
        self.project_parameters = None
        self.project_name = ""

    def process_folder(self, current_path, full_folder_path):
        """
        Recursively process the handlebars templates for the given project.
        """
        for file_name in os.listdir(full_folder_path):
            file: ParsedFile = parse_file_name(file_name, self.project_parameters)

            full_local_path = os.path.join(current_path, file.name)
            full_file_path = os.path.join(full_folder_path, file.original_name)

            if file_name == ".noars":
                cprint("Ignoring file        : " + ".noars", 'yellow')
                continue

            if os.path.isdir(full_file_path):
                if os.path.isdir(full_local_path):
                    cprint("Already exists folder: " + full_local_path, 'yellow')
                else:
                    cprint("Creating folder      : " + full_local_path, 'cyan')
                    os.makedirs(full_local_path)

                self.process_folder(full_local_path, full_file_path)
                continue

            if file.keep_existing and os.path.isfile(full_local_path):
                cprint("Keeping regular file : " + full_local_path, 'yellow')
                continue

            if not file.hbs_template:
                if not os.path.isfile(full_local_path):
                    cprint("Copying regular file : " + full_local_path, 'cyan')
                    copyfile(full_file_path, full_local_path)
                    continue

                if filecmp.cmp(full_file_path, full_local_path):
                    cprint("No update needed     : " + full_local_path, 'cyan')
                    continue

                # we  have  a conflict.

                full_local_path_orig = full_local_path + ".orig"
                shutil.copy(full_local_path, full_local_path_orig, follow_symlinks=True)
                shutil.copy(full_file_path, full_local_path, follow_symlinks=True)

                # if 'linux' in sys.platform:
                execute_diff(full_local_path, full_local_path_orig)

                cprint("Conflict resolved    : " + full_local_path, 'red')
                continue

            with open(full_file_path, "r", encoding='utf8') as template:
                template_content = template.read()

            template = pybars.Compiler().compile(template_content)
            content = template(self.project_parameters)

            if not os.path.isfile(full_local_path):
                cprint("Parsing HBS template : " + full_local_path, 'cyan')
                with open(full_local_path, "w", encoding='utf8') as content_file:
                    content_file.write(content)
                continue

            if content == open(full_local_path, "r", encoding='utf8').read():
                cprint("No update needed     : " + full_local_path, 'cyan')
                continue

            full_local_path_orig = full_local_path + ".orig"
            shutil.copy(full_local_path, full_local_path_orig, follow_symlinks=True)
            with open(full_local_path, "w", encoding='utf8') as content_file:
                content_file.write(content)

            # if 'linux' in sys.platform:
            execute_diff(full_local_path, full_local_path_orig)

            cprint("Conflict resolved HBS: " + full_local_path, 'red')

    def run(self):
        """
        Check if arguments were passed and if not, print a list of available projects
        """

        del sys.argv[0]

        if '-n' in sys.argv:
            self.generate_ars = False
            del sys.argv[sys.argv.index('-n')]

        if os.path.isfile(".ars"):
            with open(".ars", "r", encoding='utf8') as f:
                self.project_parameters = json.load(f)
                cprint(f"Using already existing '.ars' file settings: {self.project_parameters}",
                       'cyan')

        if not sys.argv and not self.project_parameters:
            print(colored("You need to pass a project name to generate.", "red"))

            if os.path.isdir(ARS_PROJECTS_FOLDER):
                print("Available projects (%s):" % colored(ARS_PROJECTS_FOLDER, "cyan"))
                for file_name in os.listdir(ARS_PROJECTS_FOLDER):
                    if os.path.isdir(os.path.join(ARS_PROJECTS_FOLDER, file_name)):
                        print(f" * {file_name}")
            else:
                print(f"{ARS_PROJECTS_FOLDER} folder doesn't exist.")

            sys.exit(1)

        # if we have arguments, we need to either create, or augument the projectParameters
        # with the new settings.
        if sys.argv:
            self.project_parameters = self.project_parameters if self.project_parameters else dict()
            self.project_parameters['NAME'] = sys.argv[0]

            del sys.argv[0]

        # we iterate the rest of the parameters, and augument the projectParameters
        for i in range(len(sys.argv)):
            m = PARAM_RE.match(sys.argv[i])
            param_name = m.group(1)
            param_value = m.group(3) if m.group(3) else True

            self.project_parameters[param_name] = param_value
            self.project_parameters[f"arg{i}"] = sys.argv[i]

        self.project_name = self.project_parameters["NAME"]

        """
        Generate the actual project.
        """
        print(f"Generating {self.project_name} with {self.project_parameters}")

        if not os.path.isfile(os.path.join(ARS_PROJECTS_FOLDER, self.project_name, ".noars")) \
                and self.generate_ars:

            with open(".ars", "w", encoding='utf8') as json_file:
                json.dump(self.project_parameters, json_file)

        self.process_folder(".", os.path.join(ARS_PROJECTS_FOLDER, self.project_name))


def main():
    Main().run()
