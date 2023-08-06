#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import ast
import io
import os
import sys
import re
from shutil import rmtree

from setuptools import find_packages, setup, Command

# parse version from locust/__init__.py
_version_re = re.compile(r'__version__\s+=\s+(.*)')
_version_file = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "locust_nest",
        "version.py")
with open(_version_file, 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

# Package meta-data.
NAME = 'locust-nest'
DESCRIPTION = 'Auto-import and compilation of locust TaskSets.'
URL = 'https://github.com/ps-george/locust-nest'
EMAIL = 'puntersg@gmail.com'
AUTHOR = 'George Punter'
REQUIRES_PYTHON = '>=2.7.0'
VERSION = version


def get_requirements(remove_links=True):
    """
    lists the requirements to install.
    """
    requirements = []
    try:
        with open('requirements.txt') as f:
            requirements = f.read().splitlines()
    except Exception as ex:
        with open('DecoraterBotUtils.egg-info\requires.txt') as f:
            requirements = f.read().splitlines()
    if remove_links:
        for requirement in requirements:
            # git repository url.
            if requirement.startswith("git:"):
                requirements.remove(requirement)
    return requirements

# What packages are required for this module to be executed?
REQUIRED = get_requirements()
print("Requires:\n{}".format(REQUIRED))

def get_links():
    """
    gets URL Dependency links.
    """
    links_list = get_requirements(remove_links=False)
    for link in links_list:
        # git repository url.
        if not link.startswith("git:"):
            links_list.remove(link)
    return links_list

DEPENDENCY_LINKS = get_links()

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!
with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system(
            '{0} setup.py sdist bdist_wheel --universal'.format(sys.executable)
        )

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')
        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    package_data={'locust_nest': ['example/*']},
    install_requires=REQUIRED,
    dependency_links=DEPENDENCY_LINKS,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
    entry_points={
        'console_scripts': [
            'locust-nest = locust_nest.main:main',
        ]
    }
)
