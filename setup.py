#!/usr/bin/python3

import sys
import os
from setuptools import setup, find_packages


def get_requirements():
    with open('requirements.txt') as fd:
        return fd.read().splitlines()


def get_version():
    with open(os.path.join('thoth_solver', '__init__.py')) as f:
        content = f.readline()

    for line in content:
        if line.startswith('__version__ ='):
            # dirty, remove trailing and leading chars
            return line.split(' = ')[1][1:-2]


def get_long_description():
    with open('README.rst', 'r') as f:
        return f.read()


setup(
    name='thoth-solver',
    version=get_version(),
    entry_points={
        'console_scripts': ['thoth-solver=thoth_solver.cli:cli']
    },
    packages=find_packages(),
    install_requires=get_requirements(),
    author='Fridolin Pokorny',
    author_email='fridolin@redhat.com',
    maintainer='Fridolin Pokorny',
    maintainer_email='fridolin@redhat.com',
    description='Tool and library for discovering package dependencies in PyPI world',
    long_description=get_long_description(),
    url='https://github.com/fridex/thoth-solver',
    license='ASL v2.0',
    keywords='python dependency pypi dependencies tool library',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy"
    ]
)
