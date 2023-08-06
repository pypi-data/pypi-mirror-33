#!/usr/bin/env python
import codecs
import os.path
import re
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


requires = ['requests==2.18.4', "eth-keyfile==0.5.0", "secp256k1==0.13.2"]

setup_options = {
    'name': 'icxcli', 'version': find_version("icxcli", "__init__.py"),
    'description': 'A Universal Command Line Environment for ICON.',
    'long_description': open('README.rst').read(),
    'author': 'ICON foundation',
    'author_email': 'foo@icon.foundation',
    'url': 'https://github.com/icon-project/icon_cli_tool',
    'scripts': ['bin/icli'],
    'packages': find_packages(exclude=['tests*']),
    'package_data': {'icxcli': ['README.rst', 'cmd/network_conf.json'] },
    'license': "Apache License 2.0",
    'install_requires': requires,
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6'
    ]
}

setup(**setup_options)
