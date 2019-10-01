#!/usr/bin/env python3
# thoth-solver
# Copyright(C) 2019 Fridolin Pokorny
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

"""Test resolving versions given the version range in Python ecosystem."""

import pytest
from base import SolverTestCase
from thoth.python import Source
from thoth.solver.python.python_solver import PythonSolver


class TestPythonSolver(SolverTestCase):
    """Test resolving version ranges in the Python ecosystem."""

    _PYPI_SIMPLE_API_URL = "https://pypi.org/simple"

    _SELINON_VERSIONS = {
        "selinon": {
            ("0.1.0rc2", "https://pypi.org/simple"),
            ("0.1.0rc3", "https://pypi.org/simple"),
            ("0.1.0rc4", "https://pypi.org/simple"),
            ("0.1.0rc5", "https://pypi.org/simple"),
            ("0.1.0rc6", "https://pypi.org/simple"),
            ("0.1.0rc7", "https://pypi.org/simple"),
            ("0.1.0rc8", "https://pypi.org/simple"),
            ("0.1.0rc9", "https://pypi.org/simple"),
            ("1.0.0rc1", "https://pypi.org/simple"),
            ("1.0.0rc2", "https://pypi.org/simple"),
            ("1.0.0rc3", "https://pypi.org/simple"),
            ("1.0.0rc4", "https://pypi.org/simple"),
            ("1.0.0", "https://pypi.org/simple"),
            ("1.1.0", "https://pypi.org/simple"),
        }
    }

    @pytest.mark.parametrize(
        "package_specification,resolved_versions,all_versions",
        [
            ("selinon<=1.1.0", _SELINON_VERSIONS, True),
            ("selinon<=1.0.0", {"selinon": {"1.0.0", "https://pypi.org/simple"}}, False),
            ("tensorflow==2.0.0", {"tensorflow": {("2.0.0", "https://pypi.org/simple")}}, True),
        ],
    )
    def test_solve_dependencies(self, package_specification, resolved_versions, all_versions):
        solver = PythonSolver(fetcher_kwargs={"source": Source(self._PYPI_SIMPLE_API_URL)})
        test_resolved_versions = solver.solve([package_specification], all_versions=all_versions)
        test_resolved_versions = {k: set(v) for k, v in test_resolved_versions.items()}
        assert test_resolved_versions == resolved_versions
