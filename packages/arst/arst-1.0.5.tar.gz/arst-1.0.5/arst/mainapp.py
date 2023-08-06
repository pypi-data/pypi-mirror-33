import filecmp
import json
import os
import shutil
import sys
import pybars
import colorama
import subprocess
import re
from typing import Dict, Optional
import argparse
from textwrap import dedent

from .program_arguments import ProgramArguments
from .file_resolver import FileResolver
from .project_reader import ProjectDefinition, read_project_definition
from .color_functions import cyan, red, yellow
from .command_push import push_files_to_template
from .command_tree import display_project_tree

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
        self.name = original_name
        self.original_name = original_name
        self.keep_existing = False
        self.hbs_template = False


def parse_file_name(file_name: str, project_parameters: Dict[str, str]) -> ParsedFile:
    """
    parseFileName - Parse the fie name
    :param file_name: string with filename
    :param project_parameters: the project parameters if they are used in the file name.
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


def execute_diff(file1: str, file2: str) -> None:
    """
    Run an external diff program on the two files
    """
    subprocess.call([ARS_DIFF_TOOL, file1, file2])


def process_folder(current_path: str,
                   file_resolver: FileResolver,
                   project_parameters: Dict[str, str]) -> None:
    """
    Recursively process the handlebars templates for the given project.
    """
    for file_entry in file_resolver.listdir():
        file: ParsedFile = parse_file_name(file_entry.name, project_parameters)

        full_local_path = os.path.join(current_path, file.name)
        full_file_path = file_entry.absolute_path

        if file_entry.name == "HELP.md" or file_entry.name == ".ars":
            print(yellow("Ignoring file        :"),
                  yellow(file_entry.name, bold=True))
            continue

        if file_entry.is_dir:
            if os.path.isdir(full_local_path):
                print(cyan("Already exists folder:"),
                      cyan(full_local_path, bold=True))
            else:
                print(yellow("Creating folder      :"),
                      yellow(full_local_path, bold=True))
                os.makedirs(full_local_path)

            process_folder(full_local_path,
                           file_resolver.subentry(file_entry),
                           project_parameters)
            continue

        if file.keep_existing and os.path.isfile(full_local_path):
            print(cyan("Keeping regular file :"),
                  cyan(full_local_path, bold=True))
            continue

        if not file.hbs_template:
            if not os.path.isfile(full_local_path):
                print(yellow("Copying regular file :"),
                      yellow(full_local_path, bold=True))
                shutil.copy(full_file_path, full_local_path)
                continue

            if filecmp.cmp(full_file_path, full_local_path):
                print(cyan("No update needed     :"),
                      cyan(full_local_path, bold=True))
                continue

            # we  have  a conflict.
            full_local_path_orig = full_local_path + ".orig"
            shutil.copy(full_local_path, full_local_path_orig, follow_symlinks=True)
            shutil.copy(full_file_path, full_local_path, follow_symlinks=True)

            # if 'linux' in sys.platform:
            execute_diff(full_local_path, full_local_path_orig)

            print(red("Conflict resolved    :"),
                  red(full_local_path, bold=True))
            continue

        with open(full_file_path, "r", encoding='utf8') as template_file:
            template_content = template_file.read()

        template = pybars.Compiler().compile(template_content)
        content = template(project_parameters)

        if not os.path.isfile(full_local_path):
            print(yellow("Parsing HBS template :"),
                  yellow(full_local_path, bold=True))

            with open(full_local_path, "w", encoding='utf8') as content_file:
                content_file.write(content)

            shutil.copystat(full_file_path, full_local_path)

            continue

        if content == open(full_local_path, "r", encoding='utf8').read():
            print(cyan("No update needed     :"),
                  cyan(full_local_path, bold=True))
            continue

        full_local_path_orig = full_local_path + ".orig"
        shutil.copy(full_local_path, full_local_path_orig, follow_symlinks=True)
        with open(full_local_path, "w", encoding='utf8') as content_file:
            content_file.write(content)

        # if 'linux' in sys.platform:
        execute_diff(full_local_path, full_local_path_orig)

        print(red("Conflict resolved HBS:"),
              red(full_local_path, bold=True))


def run_mainapp():
    """
    Run the main application.

    Implicitly the command will try to generate a project from one of the given
    templates.
    """
    global project_parameters

    parser = argparse.ArgumentParser(description="Poor man's yo for quick project generation.")
    parser.add_argument("-n", "--noars", default=False, action="store_true", help="Don't generate the .ars file.")
    parser.add_argument("-v", "--version", default=False, action="store_true", help="Show the project version.")
    parser.add_argument("template", help="The template/command to generate/run.", nargs="?")
    parser.add_argument("parameter", help="Generation parameters.", nargs='*')

    args: ProgramArguments = parser.parse_args()

    loaded_project_parameters: Optional[Dict[str, str]] = None

    if args.version:
        print(cyan(dedent("""\
                                    _     _
          __ _ _ __ ___  ___  _ __ (_)___| |_
         / _` | '__/ __|/ _ \| '_ \| / __| __|
        | (_| | |  \__ \ (_) | | | | \__ \ |_
         \__,_|_|  |___/\___/|_| |_|_|___/\__|
                               version: 1.0.5
        """), bold=True))
        sys.exit(0)

    if args.template == "push":
        push_files_to_template(ARS_PROJECTS_FOLDER, args)
        sys.exit(0)

    if args.template == "tree":
        display_project_tree(ARS_PROJECTS_FOLDER, args)
        sys.exit(0)

    if os.path.isfile(".ars"):
        with open(".ars", "r", encoding='utf8') as f:
            loaded_project_parameters = json.load(f)
            print(cyan("Using already existing"),
                  cyan("'.ars'", bold=True),
                  cyan("file settings:"),
                  cyan(loaded_project_parameters, bold=True))

    if not args.template and not loaded_project_parameters:
        print(red("You need to pass a project name to generate."))

        if os.path.isdir(ARS_PROJECTS_FOLDER):
            print("Available projects (%s):" % cyan(ARS_PROJECTS_FOLDER))
            for file_name in os.listdir(ARS_PROJECTS_FOLDER):
                if os.path.isdir(os.path.join(ARS_PROJECTS_FOLDER, file_name)):
                    print(f" * {file_name}")
        else:
            print(f"{ARS_PROJECTS_FOLDER} folder doesn't exist.")

        sys.exit(1)

    # if we have arguments, we need to either create, or augument the projectParameters
    # with the new settings.
    project_parameters = loaded_project_parameters if loaded_project_parameters else dict()

    if args.template:
        project_parameters['NAME'] = args.template

    # we iterate the rest of the parameters, and augument the projectParameters
    for i in range(len(args.parameter)):
        m = PARAM_RE.match(args.parameter[i])
        param_name = m.group(1)
        param_value = m.group(3) if m.group(3) else True

        project_parameters[param_name] = param_value
        project_parameters[f"arg{i}"] = args.parameter[i]

    project_name = project_parameters["NAME"]

    project_definition: ProjectDefinition = read_project_definition(ARS_PROJECTS_FOLDER, project_name)

    # Generate the actual project.
    print(cyan("Generating"),
          cyan(project_name, bold=True),
          cyan("with"),
          cyan(project_parameters, bold=True))

    if project_definition.generate_ars and not args.noars:
        with open(".ars", "w", encoding='utf8') as json_file:
            json.dump(project_parameters, json_file)

    process_folder(".", project_definition.file_resolver(), project_parameters)


def main():
    try:
        colorama.init()
        run_mainapp()
    finally:
        colorama.deinit()
