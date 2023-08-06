"""
Init a new Python module
"""

import os
import sys
import venv
import shutil
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Initiate a Python module.")
    parser.add_argument("project_name", help="Name of the project")
    parser.add_argument(
        "-s", "--simple_project", help="Simple project", action="store_false"
    )
    args = parser.parse_args()

    MODULE_FOLDER = os.path.dirname(os.path.abspath(__file__))
    EXECUTION_FOLDER = os.getcwd()

    print(MODULE_FOLDER)
    # Project's folder creation
    try:
        os.mkdir(args.project_name)
    except FileExistsError:
        sys.exit("A folder with the project's name already exists")

    # Enter the project's folder
    os.chdir(args.project_name)

    # Git init
    os.system("git init")

    # Virtual environnement creation
    new_env = venv.EnvBuilder(with_pip=True)
    new_env.create(".env")

    # Download common modules
    os.system(".env/bin/pip install pylint black")

    # Create vscode workspace
    os.mkdir(".vscode")

    shutil.copyfile(
        MODULE_FOLDER + "/initproject/include/settings.json",
        EXECUTION_FOLDER + "/" + args.project_name + "/.vscode/settings.json",
    )

    shutil.copyfile(
        MODULE_FOLDER + "/initproject/include/initproject.code-workspace",
        EXECUTION_FOLDER
        + "/"
        + args.project_name
        + "/"
        + args.project_name
        + ".code-workspace",
    )

    # Create git ignore
    shutil.copyfile(
        MODULE_FOLDER + "/initproject/include/.gitignore",
        EXECUTION_FOLDER + "/" + args.project_name + "/.gitignore",
    )

    # Create folder tree and files

    if args.simple_project:
        with open(args.project_name + ".py", "w") as file:
            pass
    else:
        os.mkdir(args.project_name)
        os.mkdir("tests")
        os.mkdir("docs")
        with open(args.project_name + "/__init__.py", "w") as file:
            pass

