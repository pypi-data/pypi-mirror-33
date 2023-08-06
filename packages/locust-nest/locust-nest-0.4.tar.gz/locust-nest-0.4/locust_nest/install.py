import os
from shutil import copy
import sys
import argparse
from helpers import retry_valid_input
import pkg_resources

DATA_PATH = pkg_resources.resource_filename('locust_nest', 'example/') 


def install_parser():
    """Create parser object used for defining all options for Locust.

    Returns:
        OptionParser: OptionParser object used in *parse_options*.
    """

    # Initialize
    parser = argparse.ArgumentParser(usage="locust-nest [dir]")
    return parser


def install(args=[]):
    """Install locust-nest example file and config for a repository.

    """

    if args:
        dir_name = args[0]
    else:
        dir_name = retry_valid_input(
            "Enter the directory name for your load tests:",
            title='dir',
            default='loadtests/'
            )

    if not os.path.exists(dir_name):
        print("Creating directory {}".format(dir_name))
        os.makedirs(dir_name)
    else:
        print("{} already exists, skipping create directory.".format(dir_name))

    # Copy files into dir: README, example file
    files = ['example.py', 'README.md', 'run_load_tests.sh']
    for i, file_path in enumerate(map(lambda f: DATA_PATH + f, files)):
        if os.path.exists(os.path.join(dir_name, files[i])):
            print("{} already exists, skipping copy.".format(file_path))
        else:
            print("Copying {} into {}".format(files[i], dir_name))
            copy(file_path, dir_name)
