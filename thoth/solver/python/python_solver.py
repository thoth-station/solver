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

import attr
from thoth.python import Source
from packaging.requirements import Requirement

from .base import DependencyParser
from .base import ReleasesFetcher
from .base import Solver

from .._typing import MYPY_CHECK_RUNNING

if MYPY_CHECK_RUNNING:  # pragma: no cover
    from typing import List, Tuple


_LOGGER = logging.getLogger(__name__)


@attr.s(slots=True)
class PythonReleasesFetcher(ReleasesFetcher):
    """A releases fetcher based on PEP compatible simple API (also supporting Warehouse API)."""

    source = attr.ib(type=Source, kw_only=True)

    def fetch_releases(self, package_name):  # type: (str) -> Tuple[str, List[Tuple[str, str]]]
        """Fetch package and index_url for a package_name."""
        package_name = self.source.normalize_package_name(package_name)  # XXX
        releases = self.source.get_package_versions(package_name)
        releases_with_index_url = [(release, self.index_url) for release in releases]
        return package_name, releases_with_index_url

    @property
    def index_url(self):  # type: () -> str
        """Get URL to package source index from where releases are fetched."""
        url = self.source.url  # type: str
        return url


@attr.s(slots=True)
class PythonDependencyParser(DependencyParser):
    """Python Dependency parsing."""

    @staticmethod
    def parse_python(spec):  # type: (str) -> Requirement
        """Parse PyPI specification of a single dependency.

        :param spec: str, for example "Django>=1.5,<1.8"
        :return: requirement for the Python package
        """
        return Requirement(spec)

    def parse(self, specs):  # type: (List[str]) -> List[Requirement]
        """Parse specs."""
        return [self.parse_python(s) for s in specs]


@attr.s(slots=True)
class PythonSolver(Solver):
    """PyPI dependencies solver."""

    dependency_parser = attr.ib(type=PythonDependencyParser, kw_only=True)
    releases_fetcher = attr.ib(type=PythonReleasesFetcher, kw_only=True)
