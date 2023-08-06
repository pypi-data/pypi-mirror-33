# -*- coding: utf-8 -*-

### imports ###################################################################
import logging
import os

### imports from ##############################################################
from setuptools import setup, find_packages

###############################################################################
AUTHOR = 'hirschbeutel'
AUTHOR_EMAIL = 'hirschbeutel@gmail.com'

classifiers = [
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',        
        ]

DESCRIPTION = 'LMI GFM FD3 filereader'
LONG_DESCRIPTION = 'LMI GFM ODSCAD API MikorCad premium 3D sensor Alligator FD3 OMC'
PACKAGE_NAME = 'mikrocad'
URL = 'https://bitbucket.org/hirschbeutel/mikrocad'


def read_package_variable(key, filename='__init__.py'):
    """Read the value of a variable from the package without importing."""
    module_path = os.path.join(PACKAGE_NAME, filename)

    with open(module_path) as module:
        for line in module:
            parts = line.strip().split(' ', 2)

            if parts[:-1] == [key, '=']:
                return parts[-1].strip("'")

    logging.warning("'%s' not found in '%s'", key, module_path)
    return None

setup(
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        classifiers=classifiers,
        description=DESCRIPTION,
        license='MIT',
        long_description=LONG_DESCRIPTION,
        name=read_package_variable('__project__'),
        packages=find_packages(),
        url=URL,
        version=read_package_variable('__version__'),
)
