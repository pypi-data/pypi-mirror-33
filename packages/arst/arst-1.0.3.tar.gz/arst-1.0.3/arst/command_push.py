import sys
import shutil
import os.path

from .program_arguments import ProgramArguments
from .color_functions import red, yellow


def push_files_to_template(projects_folder: str,
                           args: ProgramArguments) -> None:

    if not args.parameter or len(args.parameter) < 2:
        print(red("Invalid number of parameters sent to push. Send at least project + 1 file"))
        sys.exit(1)

    project_name = args.parameter[0]

    for file_name in args.parameter[1:]:
        print(yellow("Pushing"),
              yellow(file_name, bold=True),
              yellow("to"),
              yellow(project_name, bold=True))
        shutil.copy(file_name, os.path.join(projects_folder, project_name, file_name))
