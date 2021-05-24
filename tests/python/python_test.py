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

"""Test solver for Python ecosystem."""

import pytest
import json
from pathlib import Path
from tests.base_test import SolverTestCase

from thoth.solver.python.python import extract_metadata
from thoth.solver.python.python import parse_requirement_str
from thoth.solver.python.python import _pipdeptree as pipdeptree
from thoth.solver.python.python import get_environment_packages


class TestPython(SolverTestCase):
    """Test solving Python dependencies."""

    _WINCERTSTORE_REQUIREMENT = {
        "package_name": "wincertstore",
        "normalized_package_name": "wincertstore",
        "specifier": "==0.2",
        "resolved_versions": [],
        "extras": [],
        "extra": ["ssl"],
        "marker": 'sys_platform == "win32" and sys_platform == "linux" and extra == "ssl"',
        "marker_evaluated": 'sys_platform == "win32" and sys_platform == "linux" and python_version >= "0.0"',
        "marker_evaluation_result": False,
        "marker_evaluation_error": None,
    }

    _XONSH_REQUIREMENT = {
        "package_name": "xonsh",
        "normalized_package_name": "xonsh",
        "specifier": None,
        "resolved_versions": [],
        "extras": [],
        "extra": [],
        "marker": 'python_version >= "2.0"',
        "marker_evaluated": 'python_version >= "2.0"',
        "marker_evaluation_result": True,
        "marker_evaluation_error": None,
    }

    _DELEGATOR_PY_REQUIREMENT = {
        "package_name": "delegator-py",
        "normalized_package_name": "delegator-py",
        "specifier": "<=0.0",
        "resolved_versions": [],
        "extras": [],
        "extra": [],
        "marker": None,
        "marker_evaluated": None,
        "marker_evaluation_result": True,
        "marker_evaluation_error": None,
    }

    _SELINON_REQUIREMENT = {
        "extra": ["workflow"],
        "extras": {"redis", "postgresql"},
        "marker": 'extra == "workflow"',
        "marker_evaluated": 'python_version >= "0.0"',
        "marker_evaluation_error": None,
        "marker_evaluation_result": True,
        "normalized_package_name": "selinon",
        "package_name": "selinon",
        "resolved_versions": [],
        "specifier": "==1.1.0",
    }

    @pytest.mark.parametrize(
        "metadata_file_path,metadata_file_extracted_path",
        [("tensorflow.json", "tensorflow_extracted.json")],
    )
    def test_extract_metadata(self, metadata_file_path, metadata_file_extracted_path):
        """Test extracted metadata."""
        metadata = json.loads((Path(self.data_dir) / "metadata" / metadata_file_path).read_text())
        metadata_extracted = json.loads((Path(self.data_dir) / "metadata" / metadata_file_extracted_path).read_text())
        assert extract_metadata(metadata, "https://pypi.org/simple") == metadata_extracted

    @pytest.mark.parametrize(
        "requirement_str,expected_requirement",
        [
            (
                # Make disjoint platforms so we always evaluate the marker to False.
                'wincertstore (==0.2) ; (sys_platform == "win32") and (sys_platform == "linux") and extra == \'ssl\'',
                _WINCERTSTORE_REQUIREMENT,
            ),
            ('xonsh ; (python_version >= "2.0")', _XONSH_REQUIREMENT),
            ("delegator-py (<=0.0)", _DELEGATOR_PY_REQUIREMENT),
            ("selinon[postgresql,redis] (==1.1.0); extra == 'workflow'", _SELINON_REQUIREMENT),
        ],
    )
    def test_parse_requirement_str(self, requirement_str, expected_requirement):
        """Test parse requirement string."""
        result = parse_requirement_str(requirement_str)
        if result.get("extras"):
            result["extras"] = set(result["extras"])
        assert result == expected_requirement

    def test_pipdeptree_one(self, venv):
        """Test pipdetree one."""
        venv.install("selinon==1.1.0")
        output = pipdeptree(venv.python, "selinon")
        assert "dependencies" in output
        output.pop("dependencies")
        assert output == {"package": {"package_name": "selinon", "key": "selinon", "installed_version": "1.1.0"}}

    def test_pipdeptree_multiple(self, venv):
        """Test pipdetree multiple."""
        venv.install("selinon==1.1.0")
        output = pipdeptree(venv.python)
        assert len(output) > 1

    def test_get_environment_packages(self, venv):
        """Test get environment packages."""
        venv.install("selinon==1.1.0")
        assert {"package_name": "selinon", "package_version": "1.1.0"} in get_environment_packages(venv.python)
