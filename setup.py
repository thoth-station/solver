#!/usr/bin/env python3
"""Setup file."""
import os
import sys
from setuptools import setup
from pathlib import Path
from setuptools.command.test import test as TestCommand


def get_requirements():
    """Get requirements."""
    with open("requirements.txt") as fd:
        return fd.read().splitlines()


def get_version():
    """Get version."""
    with open(os.path.join("thoth", "solver", "__init__.py")) as f:
        content = f.readlines()

    for line in content:
        if line.startswith("__version__ ="):
            # dirty, remove trailing and leading chars
            return line.split(" = ")[1][1:-2]

    raise ValueError("No package version found")


class Test(TestCommand):
    """Introduce test command to run testsuite using pytest."""

    _IMPLICIT_PYTEST_ARGS = [
        "--timeout=30",
        "--cov=./thoth",
        "--cov-report=xml",
        "--capture=no",
        "--mypy",
        "thoth",
        "--verbose",
        "-l",
        "-s",
        "-vv",
        "tests/",
    ]

    user_options = [("pytest-args=", "a", "Arguments to pass into py.test")]

    def initialize_options(self):
        """Initialize options."""
        super().initialize_options()
        self.pytest_args = None

    def finalize_options(self):
        """Finalize options."""
        super().finalize_options()
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """Run tests."""
        import pytest

        passed_args = list(self._IMPLICIT_PYTEST_ARGS)

        if self.pytest_args:
            self.pytest_args = [arg for arg in self.pytest_args.split() if arg]
            passed_args.extend(self.pytest_args)

        sys.exit(pytest.main(passed_args))


VERSION = get_version()
setup(
    name="thoth-solver",
    version=VERSION,
    entry_points={"console_scripts": ["thoth-solver=thoth.solver.cli:cli"]},
    packages=["thoth.solver", "thoth.solver.python"],
    install_requires=get_requirements(),
    author="Fridolin Pokorny",
    author_email="fridolin@redhat.com",
    maintainer="Fridolin Pokorny",
    maintainer_email="fridolin@redhat.com",
    description="Tool and library for discovering package dependencies in PyPI world",
    long_description=Path("README.rst").read_text(),
    url="https://github.com/thoth-station/solver",
    license="GPLv3+",
    keywords="python dependency pypi dependencies tool library",
    zip_safe=False,
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
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    command_options={"build_sphinx": {"version": ("setup.py", VERSION), "release": ("setup.py", VERSION)}},
    package_data={"thoth.solver": ["py.typed"]},
    cmdclass={"test": Test},
)
