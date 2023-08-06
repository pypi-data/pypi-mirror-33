"""Build or install wheel packages for passing customize code between modules"""

__version__ = '0.2.0'

import os
from subprocess import call

# calling pip3.6 in CentOS container
pip_command = 'pip' if os.name == 'nt' else 'pip3.6'


def build_wheels(target_dir: str):
    """
    Build wheels to target directory, need to locate current file in setup.py folder
    :param target_dir:
    :return:
    """
    call([f'{pip_command}', 'wheel', '.', '--wheel-dir', target_dir])


def install_requirements(dir_name: str):
    """
    install all the wheels in dir_name, find all the wheel files by '*.whl'
    :param dir_name:
    """
    for whl_file in find_whl_files(dir_name):
        print(f'installing package {whl_file}')
        install_package(whl_file)


def find_whl_files(input_dir):
    whl_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".whl"):
                whl_files.append(os.path.join(root, file))
    return whl_files


def install_package(whl_path):
    print(f'installing {whl_path}')
    call([f'{pip_command}', 'install', '--upgrade', '--force-reinstall', whl_path])
