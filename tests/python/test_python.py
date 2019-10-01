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

"""Test solver for Python ecosystem."""

import os
import pytest
import json
from pathlib import Path
from base import SolverTestCase
import responses
from urllib.parse import urlparse
from urllib.parse import parse_qs

from thoth.solver.python.python import extract_metadata
from thoth.solver.python.python import parse_requirement_str
from thoth.solver.python.python import pipdeptree
from thoth.solver.python.python import should_resolve_subgraph
from thoth.solver.python.python import get_environment_packages


class TestPython(SolverTestCase):
    """Test solving Python dependencies."""

    _WINCERTSTORE_REQUIREMENT = {
        "extras": ["ssl"],
        "marker": 'sys_platform == "win32" and sys_platform == "linux" and python_version >= "0.0"',
        "marker_evaluation_error": None,
        "marker_evaluation_result": False,
        "normalized_package_name": "wincertstore",
        "package_name": "wincertstore",
        "parsed_markers": [
            [{"op": "==", "value": "win32", "variable": "sys_platform"}],
            "and",
            [{"op": "==", "value": "linux", "variable": "sys_platform"}],
            "and",
            {"op": ">=", "value": "0.0", "variable": "python_version"},
        ],
        "resolved_versions": [],
        "specifier": "==0.2",
    }

    _XONSH_REQUIREMENT = {
        "extras": [],
        "marker": 'python_version >= "2.0"',
        "marker_evaluation_error": None,
        "marker_evaluation_result": True,
        "normalized_package_name": "xonsh",
        "package_name": "xonsh",
        "parsed_markers": [[{"op": ">=", "value": "2.0", "variable": "python_version"}]],
        "resolved_versions": [],
        "specifier": None,
    }

    _DELEGATOR_PY_REQUIREMENT = {
        "extras": [],
        "marker": None,
        "marker_evaluation_error": None,
        "marker_evaluation_result": True,
        "normalized_package_name": "delegator-py",
        "package_name": "delegator-py",
        "parsed_markers": [],
        "resolved_versions": [],
        "specifier": "<=0.0",
    }

    @pytest.mark.parametrize(
        "metadata_file_path,metadata_file_extracted_path", [("tensorflow.json", "tensorflow_extracted.json")]
    )
    def test_extract_metadata(self, metadata_file_path, metadata_file_extracted_path):
        metadata = json.loads((Path(self.data_dir) / "metadata" / metadata_file_path).read_text())
        metadata_extracted = json.loads((Path(self.data_dir) / "metadata" / metadata_file_extracted_path).read_text())
        assert extract_metadata(metadata) == metadata_extracted

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
        ],
    )
    def test_parse_requirement_str(self, requirement_str, expected_requirement):
        assert parse_requirement_str(requirement_str) == expected_requirement

    def test_pipdeptree_one(self, venv):
        venv.install("selinon==1.1.0")
        output = pipdeptree(venv.python, "selinon")
        assert "dependencies" in output
        output.pop("dependencies")
        assert output == {"package": {"package_name": "selinon", "key": "selinon", "installed_version": "1.1.0"}}

    def test_pipdeptree_multiple(self, venv):
        venv.install("selinon==1.1.0")
        output = pipdeptree(venv.python)
        assert len(output) > 1

    @responses.activate
    def test_should_resolve_subgraph_no(self):
        def request_callback(request):
            parsed_url = urlparse(request.url)
            query = parse_qs(parsed_url.query)
            assert query.get("package_name") == ["tensorflow"]
            assert query.get("package_version") == ["2.0.0"]
            assert query.get("index_url") == ["https://pypi.org/simple"]
            assert query.get("solver_name") == ["solver-ubi-8-py36"]
            return 208, {}, "{}"

        assert "THOTH_SOLVER" not in os.environ
        url = "http://localhost"
        responses.add_callback(
            responses.GET,
            url,
            callback=request_callback,
            content_type='application/json',
        )
        try:
            os.environ["THOTH_SOLVER"] = "solver-ubi-8-py36"
            result = should_resolve_subgraph(url, "tensorflow", "2.0.0", "https://pypi.org/simple")
            assert result is False
            assert len(responses.calls) == 1
        finally:
            os.environ.pop("THOTH_SOLVER")

    @responses.activate
    def test_should_resolve_subgraph_yes(self):
        def request_callback(request):
            parsed_url = urlparse(request.url)
            query = parse_qs(parsed_url.query)
            assert query.get("package_name") == ["selinon"]
            assert query.get("package_version") == ["1.1.0"]
            assert query.get("index_url") == ["https://pypi.org/simple"]
            assert query.get("solver_name") == ["solver-ubi-9-py36"]
            return 200, {}, "{}"

        assert "THOTH_SOLVER" not in os.environ
        url = "http://localhost"
        responses.add_callback(
            responses.GET,
            url,
            callback=request_callback,
            content_type='application/json',
        )
        try:
            os.environ["THOTH_SOLVER"] = "solver-ubi-9-py36"
            result = should_resolve_subgraph(url, "selinon", "1.1.0", "https://pypi.org/simple")
            assert result is True
            assert len(responses.calls) == 1
        finally:
            os.environ.pop("THOTH_SOLVER")

    def test_get_environment_packages(self, venv):
        venv.install("selinon==1.1.0")
        assert {"package_name": "selinon", "package_version": "1.1.0"} in get_environment_packages(venv.python)
