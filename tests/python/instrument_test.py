#!/usr/bin/env python3
# thoth-solver
# Copyright(C) 2019 - 2021 Fridolin Pokorny
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

import json
import os
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

    @pytest.mark.parametrize(
        "package_version,package_name,distribution_name",
        [("selinon==1.1.0", "selinon", "selinon"), ("backports.weakref", "backports-weakref", "backports.weakref")],
    )
    def test_find_distribution_name(self, venv, package_version, package_name, distribution_name):
        """Test distribution name lookup."""
        venv.install(package_version)
        assert find_distribution_name(venv.python, package_name) == distribution_name

    @pytest.mark.parametrize(
        "package_name,package_version,metadata_file",
        [("delegator.py", "0.1.1", "delegator-py.json"), ("click", "7.0", "click.json")],
    )
    def test_get_package_metadata(self, venv, package_version, package_name, metadata_file):
        """Test getting package metadata."""
        with open(os.path.join(self.data_dir, "metadata", metadata_file)) as f:
            metadata = json.load(f)

        venv.install(f"{package_name}==={package_version}")
        discovered_metadata = get_package_metadata(venv.python, package_name)
        # Check the correct version is picked during the test run.
        assert discovered_metadata.get("version") == package_version
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
