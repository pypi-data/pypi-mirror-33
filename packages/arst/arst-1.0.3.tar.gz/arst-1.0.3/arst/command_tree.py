import sys

from .program_arguments import ProgramArguments
from .color_functions import red, green, blue, gray
from .project_reader import read_project_definition
from .file_resolver import FileResolver


def display_project_tree(projects_folder: str,
                         args: ProgramArguments) -> None:
    if not args.parameter or len(args.parameter) < 1:
        print(red("Invalid number of parameters sent to tree. Specify project."))
        sys.exit(1)

    project_name = args.parameter[0]

    project_definition = read_project_definition(projects_folder=projects_folder,
                                                 project_name=project_name)
    file_resolver = project_definition.file_resolver()
    display_current_folder(file_resolver)


def display_current_folder(file_resolver: FileResolver, indent: int=0) -> None:
    for entry in file_resolver.listdir():
        if entry.is_dir:
            print("  " * indent + blue(entry.name) + gray(f" ({entry.owning_project})"))
            display_current_folder(file_resolver.subentry(entry), indent + 1)
        elif entry.is_exe:
            print("  " * indent + green(entry.name) + gray(f" ({entry.owning_project})"))
        else:
            print("  " * indent + entry.name + gray(f" ({entry.owning_project})"))
