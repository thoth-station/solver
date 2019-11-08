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
import abc

from thoth.python import Source

from ..exceptions import NoReleasesFound
from ..exceptions import SolverException
from .._typing import MYPY_CHECK_RUNNING

if MYPY_CHECK_RUNNING:  # pragma: no cover
    from typing import List, Tuple, Dict
    from packaging.requirements import Requirement


_LOGGER = logging.getLogger(__name__)


@attr.s(slots=True)
class ReleasesFetcher:
    """A base class for fetching package releases."""

    @abc.abstractmethod
    def fetch_releases(self, package):  # type: (str) -> Tuple[str, List[Tuple[str, str]]]
        """Abstract method for getting list of releases versions."""

    @abc.abstractmethod
    def index_url(self):  # type: () -> str
        """Get URL to index from where releases are fetched."""


@attr.s(slots=True)
class DependencyParser:
    """Base class for Dependency parsing."""

    @abc.abstractmethod
    def parse(self, specs):  # type: (List[str]) -> List[Requirement]
        """Abstract method for dependency parsing."""


@attr.s(slots=True)
class Solver:
    """Base class for resolving dependencies."""

    dependency_parser = attr.ib(type=DependencyParser, kw_only=True)
    releases_fetcher = attr.ib(type=ReleasesFetcher, kw_only=True)

    def solve(self, dependencies, graceful=True):  # type: (List[str], bool) -> Dict[str, List[Tuple[str, str]]]
        """Solve `dependencies` against a repository."""
        solved = {}  # type: Dict[str, List[Tuple[str, str]]]
        for dep in self.dependency_parser.parse(dependencies):
            _LOGGER.debug("Fetching releases for: %r", dep)

            name, releases = self.releases_fetcher.fetch_releases(dep.name)

            if name in solved:
                raise SolverException("Dependency: {} is listed multiple times".format(name))

            if not releases:
                if graceful:
                    _LOGGER.info("No releases found for package %r", dep.name)
                    continue
                else:
                    raise NoReleasesFound("No releases found for package {!r}".format(dep.name))

            solved[name] = []
            for release in releases:
                if release[0] in dep.specifier:
                    solved[name].append(release)

            _LOGGER.debug("  matching: %s", solved[name])

        return solved


def get_ecosystem_solver(ecosystem_name):  # type: (str) -> Solver
    """Get Solver subclass instance for particular ecosystem.

    :param ecosystem_name: name of ecosystem for which solver should be get
    :return: Solver
    """
    from .python_solver import PythonSolver
    from .python_solver import PythonReleasesFetcher
    from .python_solver import PythonDependencyParser

    if ecosystem_name.lower() == "pypi":
        source = Source(url="https://pypi.org/simple", warehouse_api_url="https://pypi.org/pypi", warehouse=True)

        return PythonSolver(
            dependency_parser=PythonDependencyParser(), releases_fetcher=PythonReleasesFetcher(source=source)
        )

    raise NotImplementedError("Unknown ecosystem: {}".format(ecosystem_name))
