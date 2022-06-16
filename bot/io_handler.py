import json
from os.path import isdir, join, basename, dirname, abspath
from os import getcwd, mkdir, listdir
from shutil import rmtree
import zipfile


# import yaml


# Create temp dir for Telegram output
def get_temp_dir() -> str:
    temp_dir = join(getcwd(), 'temp')
    if not isdir(temp_dir):
        mkdir(temp_dir)
    return temp_dir


# Clear a temp dir and files when finished with it
def clr_temp_dir(dir_path: str):
    """
    :param dir_path: The location of the temp dir
    """
    rmtree(dir_path)


def create_zip_archive(file_paths: list[str], output_path: str, zip_name: str = 'archive.zip') -> str:
    """
    :param zip_name: Name of the zip archive
    :param file_paths: List of file paths to zip
    :param output_path: Path to output the zip archive (could be the temp dir)
    :return: The filepath of the zip archive
    """
    zipfile_path = join(output_path, zip_name)
    with zipfile.ZipFile(zipfile_path, 'a') as zip_file:
        for file_path in file_paths:
            zip_file.write(file_path, basename(file_path))
    return zipfile_path


def walk_dir(directory: str) -> list[str]:
    """Returns a list of full filepaths for each file n the directory"""
    return [join(directory, file) for file in listdir(directory)]


# Create logs dir if it doesn't exist in the current working directory
def get_logfile() -> str:
    log_dir = join(getcwd(), 'logs')
    if not isdir(log_dir):
        mkdir(log_dir)
    return join(log_dir, 'log.txt')


# Get administrator users (these are hardcoded)
def get_administrators() -> list[str]:
    admins_file = join(dirname(abspath(__file__)), 'administrators.json')
    with open(admins_file, 'r') as infile:
        return [admin for admin in json.loads(infile.read())['administrators']]

# DEPRECATED - Now using MySQL database
# def load_config() -> dict:
#     config_file = join(dirname(abspath(__file__)), '_config.yaml')
#     with open(config_file, 'r') as infile:
#         config = yaml.load(infile, Loader=yaml.FullLoader)
#     return config


# DEPRECATED - Now using MySQL database
# def update_config(data: dict) -> dict:
#     config_file = join(dirname(abspath(__file__)), '_config.yaml')
#     with open(config_file, 'w') as outfile:
#         yaml.dump(data, outfile)
#     return data


# DEPRECATED - Now using MySQL database
# def load_whitelist() -> list[str]:
#     whitelist_file = join(dirname(abspath(__file__)), '_whitelist.yaml')
#     with open(whitelist_file, 'r') as infile:
#         whitelist = yaml.load(infile, Loader=yaml.FullLoader)
#     return whitelist['whitelist']


# DEPRECATED - Now using MySQL database
# def update_whitelist(whitelist: list[str]) -> list[str]:
#     whitelist_file = join(dirname(abspath(__file__)), '_whitelist.yaml')
#     with open(whitelist_file, 'w') as outfile:
#         yaml.dump({'whitelist': whitelist}, outfile)
#     return whitelist
