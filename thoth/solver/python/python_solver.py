#!/usr/bin/env python3
# thoth-solver
# Copyright(C) 2018, 2019 Fridolin Pokorny
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

"""Classes for resolving dependencies as specified in each ecosystem."""

import logging

try:
    # pip<10
    from pip.req.req_file import parse_requirements
except ImportError:
    # pip>=10
    from pip._internal.req.req_file import parse_requirements
from subprocess import check_output
from tempfile import NamedTemporaryFile

from thoth.python import Source

from .base import Dependency
from .base import DependencyParser
from .base import ReleasesFetcher
from .base import Solver


_LOGGER = logging.getLogger(__name__)


class PythonReleasesFetcher(ReleasesFetcher):
    """A releases fetcher based on PEP compatible simple API (also supporting Warehouse API)."""

    def __init__(self, source: Source):
        """Initialize an instance of this class."""
        self.source = source

    def fetch_releases(self, package_name):
        """Fetch package and index_url for a package_name."""
        package_name = self.source.normalize_package_name(package_name)
        releases = self.source.get_package_versions(package_name)
        releases_with_index_url = [(item, self.index_url) for item in releases]
        return package_name, releases_with_index_url

    @property
    def index_url(self):
        """Get URL to package source index from where releases are fetched."""
        return self.source.url


class PythonDependencyParser(DependencyParser):
    """Python Dependency parsing."""

    @staticmethod
    def parse_python(spec):  # Ignore PyDocStyleBear
        """Parse PyPI specification of a single dependency.

        :param spec: str, for example "Django>=1.5,<1.8"
        :return: [Django [[('>=', '1.5'), ('<', '1.8')]]]
        """

        def _extract_op_version(spec):
            # https://www.python.org/dev/peps/pep-0440/#compatible-release
            if spec.operator == "~=":
                version = spec.version.split(".")
                if len(version) in {2, 3, 4}:
                    if len(version) in {3, 4}:
                        del version[-1]  # will increase the last but one in next line
                    version[-1] = str(int(version[-1]) + 1)
                else:
                    raise ValueError("%r must not be used with %r" % (spec.operator, spec.version))
                return [(">=", spec.version), ("<", ".".join(version))]
            # Trailing .* is permitted per
            # https://www.python.org/dev/peps/pep-0440/#version-matching
            elif spec.operator == "==" and spec.version.endswith(".*"):
                try:
                    result = check_output(["/usr/bin/semver-ranger", spec.version], universal_newlines=True).strip()
                    gte, lt = result.split()
                    return [(">=", gte.lstrip(">=")), ("<", lt.lstrip("<"))]
                except ValueError:
                    _LOGGER.warning("couldn't resolve ==%s", spec.version)
                    return spec.operator, spec.version
            # https://www.python.org/dev/peps/pep-0440/#arbitrary-equality
            # Use of this operator is heavily discouraged, so just convert it to 'Version matching'
            elif spec.operator == "===":
                return "==", spec.version
            else:
                return spec.operator, spec.version

        def _get_pip_spec(requirements):
            """There is no `specs` field In Pip 8+, take info from `specifier` field."""
            if hasattr(requirements, "specs"):
                return requirements.specs
            elif hasattr(requirements, "specifier"):
                specs = [_extract_op_version(spec) for spec in requirements.specifier]
                if len(specs) == 0:
                    # TODO: I'm not sure with this one
                    # we should probably return None instead and let pip deal with this
                    specs = [(">=", "0.0.0")]
                return specs

        _LOGGER.info("Parsing dependency %r", spec)
        # create a temporary file and store the spec there since
        # `parse_requirements` requires a file
        with NamedTemporaryFile(mode="w+", suffix="pysolve") as f:
            f.write(spec)
            f.flush()
            parsed = parse_requirements(f.name, session=f.name)
            dependency = [Dependency(x.name, _get_pip_spec(x.req)) for x in parsed].pop()

        return dependency

    def parse(self, specs):
        """Parse specs."""
        return [self.parse_python(s) for s in specs]

    @staticmethod
    def compose(deps):
        """Compose deps."""
        return DependencyParser.compose_sep(deps, ",")

    @staticmethod
    def restrict_versions(deps):
        """Not implemented."""
        return deps  # TODO


class PythonSolver(Solver):
    """Pypi dependencies solver."""

    def __init__(self, parser_kwargs=None, fetcher_kwargs=None, solver_kwargs=None):
        """Initialize instance."""
        super().__init__(
            PythonDependencyParser(**(parser_kwargs or {})),
            PythonReleasesFetcher(**(fetcher_kwargs or {})),
            **(solver_kwargs or {}),
        )
