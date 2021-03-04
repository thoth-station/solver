#!/usr/bin/env python3
# thoth-solver
# Copyright(C) 2019, 2020 Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# type: ignore

"""Test instrumentation inside a virtual environment."""

import pytest
from tests.base_test import SolverTestCase

from thoth.solver.python.instrument import find_distribution_name
from thoth.solver.python.instrument import get_package_metadata
from thoth.solver.python.instrument import execute_env_function


def _func_err():
    import sys

    print("this is error message", file=sys.stderr)
    print("this is another message", file=sys.stdout)
    sys.exit(1)


def _func_json(param):
    import json

    print(json.dumps({"foo": param}))


def _func_env():
    import os

    print(os.environ["FOO"], end="")


class TestInstrument(SolverTestCase):
    """Test instrumentation of running custom functions inside a virtual environment."""

    _DELEGATOR_PY_METADATA = {
        "entry_points": [],
        "metadata": {
            "Author": "Kenneth Reitz",
            "Author-email": "me@kennethreitz.com",
            "Classifier": [
                "Programming Language :: Python",
                "Programming Language :: Python :: 2.6",
                "Programming Language :: Python :: 2.7",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.3",
                "Programming Language :: Python :: 3.4",
                "Programming Language :: Python :: 3.5",
                "Programming Language :: Python :: 3.6",
                "Programming Language :: Python :: Implementation :: CPython",
                "Programming Language :: Python :: Implementation :: PyPy",
            ],
            "Home-page": "https://github.com/kennethreitz/delegator",
            "License": "MIT",
            "Metadata-Version": "2.1",
            "Name": "delegator.py",
            "Platform": ["UNKNOWN"],
            "Requires-Dist": ["pexpect (>=4.1.0)"],
            "Summary": "Subprocesses for Humans 2.0.",
            "Version": "0.1.1",
        },
        "requires": ["pexpect (>=4.1.0)"],
        "version": "0.1.1",
    }

    _CLICK_METADATA = {
        "entry_points": [],
        "metadata": {
            "Author": "Armin Ronacher",
            "Author-email": "armin.ronacher@active-4.com",
            "Classifier": [
                "Development Status :: 5 - Production/Stable",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: BSD License",
                "Operating System :: OS Independent",
                "Programming Language :: Python",
                "Programming Language :: Python :: 2",
                "Programming Language :: Python :: 2.7",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.4",
                "Programming Language :: Python :: 3.5",
                "Programming Language :: Python :: 3.6",
                "Programming Language :: Python :: 3.7",
            ],
            "Home-page": "https://palletsprojects.com/p/click/",
            "License": "BSD",
            "Maintainer": "Pallets Team",
            "Maintainer-email": "contact@palletsprojects.com",
            "Metadata-Version": "2.1",
            "Name": "Click",
            "Platform": ["UNKNOWN"],
            "Project-URL": [
                "Documentation, https://click.palletsprojects.com/",
                "Code, https://github.com/pallets/click",
                "Issue tracker, https://github.com/pallets/click/issues",
            ],
            "Requires-Python": ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
            "Summary": "Composable command line interface toolkit",
            "Version": "7.0",
        },
        "requires": None,
        "version": "7.0",
    }

    @pytest.mark.parametrize(
        "package_version,package_name,distribution_name",
        [("selinon==1.1.0", "selinon", "selinon"), ("backports.weakref", "backports-weakref", "backports.weakref")],
    )
    def test_find_distribution_name(self, venv, package_version, package_name, distribution_name):
        """Test distribution name lookup."""
        venv.install(package_version)
        assert find_distribution_name(venv.python, package_name) == distribution_name

    @pytest.mark.parametrize(
        "package_version, package_name, metadata",
        [("delegator.py===0.1.1", "delegator.py", _DELEGATOR_PY_METADATA), ("click===7.0", "click", _CLICK_METADATA)],
    )
    def test_get_package_metadata(self, venv, package_version, package_name, metadata):
        """Test getting package metadata."""
        venv.install(package_version)
        discovered_metadata = get_package_metadata(venv.python, package_name)
        # We don't care about files present now, just check we have some files in the output.
        assert "files" in discovered_metadata
        discovered_metadata.pop("files")
        assert discovered_metadata == metadata

    def test_package_clash(self, venv):
        """Test packages which are dependencies of this solver do not affect results of data gathering."""
        import click

        assert click.__version__ != "3.0"
        venv.install("click===3.0")
        discovered_metadata = get_package_metadata(venv.python, "click")
        assert discovered_metadata.get("version") == "3.0"

    def test_execute_env_function_raise_on_error(self, venv):
        """Assert raising an error (error propagation turned on by default)."""
        with pytest.raises(ValueError) as exc:
            execute_env_function(venv.python, _func_err)
            assert str(exc).endswith("this is error message")

    def test_execute_env_function_json(self, venv):
        """Check parsing a JSON output produced when running a function."""
        assert execute_env_function(venv.python, _func_json, is_json=True, param="bar") == {"foo": "bar"}

    def test_execute_env_function_env(self, venv):
        """Check propagation of environment variables to the underlying virtual environment."""
        assert execute_env_function(venv.python, _func_env, is_json=False, env={"FOO": "BAR"}) == "BAR"
