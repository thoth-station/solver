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

from functools import cmp_to_key
import logging

from thoth.python import Source


_LOGGER = logging.getLogger(__name__)


class SolverException(Exception):
    """Exception to be raised in Solver."""


class Tokens(object):
    """Comparison token representation."""

    operators = [">=", "<=", "==", ">", "<", "=", "!="]
    (GTE, LTE, EQ1, GT, LT, EQ2, NEQ) = range(len(operators))


def compare_version(a, b):  # Ignore PyDocStyleBear
    """Compare two version strings.

    :param a: str
    :param b: str
    :return: -1 / 0 / 1
    """

    def _range(q):
        """Convert a version string to array of integers.

        "1.2.3" -> [1, 2, 3]

        :param q: str
        :return: List[int]
        """
        r = []
        for n in q.replace("-", ".").split("."):
            try:
                r.append(int(n))
            except ValueError:
                # sort rc*, alpha, beta etc. lower than their non-annotated counterparts
                r.append(-1)
        return r

    def _append_zeros(x, num_zeros):
        """Append `num_zeros` zeros to a copy of `x` and return it.

        :param x: List[int]
        :param num_zeros: int
        :return: List[int]
        """
        nx = list(x)
        for _ in range(num_zeros):
            nx.append(0)
        return nx

    def _cardinal(x, y):
        """Make both input lists be of same cardinality.

        :param x: List[int]
        :param y: List[int]
        :return: List[int]
        """
        lx, ly = len(x), len(y)
        if lx == ly:
            return x, y
        elif lx > ly:
            return x, _append_zeros(y, lx - ly)
        else:
            return _append_zeros(x, ly - lx), y

    left, right = _cardinal(_range(a), _range(b))

    return (left > right) - (left < right)


class ReleasesFetcher(object):
    """Base class for fetching releases."""

    def fetch_releases(self, package):
        """Abstract method for getting list of releases versions."""
        raise NotImplementedError

    @property
    def index_url(self):
        """Get URL to index from where releases are fetched."""
        raise NotImplementedError


class Dependency(object):
    """A Dependency consists of (package) name and version spec."""

    def __init__(self, name, spec):
        """Initialize instance."""
        self._name = name
        # spec is a list where each item is either 2-tuple (operator, version) or list of these
        # example: [[('>=', '0.6.0'), ('<', '0.7.0')], ('>', '1.0.0')] means:
        # (>=0.6.0 and <0.7.0) or >1.0.0
        self._spec = spec

    @property
    def name(self):
        """Get name property."""
        return self._name

    @property
    def spec(self):
        """Get version spec property."""
        return self._spec

    def __contains__(self, item):
        """Implement 'in' operator."""
        return self.check(item[0])

    def __repr__(self):
        """Return string representation of this instance."""
        return "{} {}".format(self.name, self.spec)

    def __eq__(self, other):
        """Implement '==' operator."""
        return self.name == other.name and self.spec == other.spec

    def check(self, version):  # Ignore PyDocStyleBear
        """Check if `version` fits into our dependency specification.

        :param version: str
        :return: bool
        """

        def _compare_spec(spec):
            if len(spec) == 1:
                spec = ("=", spec[0])

            token = Tokens.operators.index(spec[0])
            comparison = compare_version(version, spec[1])
            if token in [Tokens.EQ1, Tokens.EQ2]:
                return comparison == 0
            elif token == Tokens.GT:
                return comparison == 1
            elif token == Tokens.LT:
                return comparison == -1
            elif token == Tokens.GTE:
                return comparison >= 0
            elif token == Tokens.LTE:
                return comparison <= 0
            elif token == Tokens.NEQ:
                return comparison != 0
            else:
                raise ValueError("Invalid comparison token")

        results, intermediaries = False, False
        for spec in self.spec:
            if isinstance(spec, list):
                intermediary = True
                for sub in spec:
                    intermediary &= _compare_spec(sub)
                intermediaries |= intermediary
            elif isinstance(spec, tuple):
                results |= _compare_spec(spec)

        return results or intermediaries


class DependencyParser(object):
    """Base class for Dependency parsing."""

    def __init__(self, **parser_kwargs):
        """Construct dependency parser."""
        if parser_kwargs:
            raise NotImplementedError

    def parse(self, specs):
        """Abstract method for Dependency parsing."""
        pass

    @staticmethod
    def compose_sep(deps, separator):
        """Opposite of parse().

        :param deps: list of Dependency()
        :param separator: when joining dependencies, use this separator
        :return: dict of {name: version spec}
        """
        result = {}
        for dep in deps:
            if dep.name not in result:
                result[dep.name] = separator.join([op + ver for op, ver in dep.spec])
            else:
                result[dep.name] += separator + separator.join([op + ver for op, ver in dep.spec])
        return result


class NoOpDependencyParser(DependencyParser):
    """Dummy dependency parser for ecosystems that don't support version ranges."""

    def parse(self, specs):
        """Transform list of dependencies (strings) to list of Dependency."""
        return [Dependency(*x.split(" ")) for x in specs]

    @staticmethod
    def compose(deps):
        """Opposite of parse()."""
        return DependencyParser.compose_sep(deps, " ")

    @staticmethod
    def restrict_versions(deps):
        """Not implemented."""
        return deps


class Solver(object):
    """Base class for resolving dependencies."""

    def __init__(self, dep_parser=None, fetcher=None, highest_dependency_version=True):
        """Initialize instance."""
        self._dependency_parser = dep_parser
        self._release_fetcher = fetcher
        self._highest_dependency_version = highest_dependency_version

    @property
    def dependency_parser(self):
        """Return DependencyParser instance used by this solver."""
        return self._dependency_parser

    @property
    def release_fetcher(self):
        """Return ReleasesFetcher instance used by this solver."""
        return self._release_fetcher

    def solve(self, dependencies, graceful=True, all_versions=False):  # Ignore PyDocStyleBear
        """Solve `dependencies` against upstream repository.

        :param dependencies: List, List of dependencies in native format
        :param graceful: bool, Print info output to stdout
        :param all_versions: bool, Return all matched versions instead of the latest
        :return: Dict[str, str], Matched versions
        """

        def _compare_version_index_url(v1, v2):
            """Get a wrapper around compare version to omit index url when sorting."""
            return compare_version(v1[0], v2[0])

        solved = {}
        for dep in self.dependency_parser.parse(dependencies):
            _LOGGER.debug("Fetching releases for: {}".format(dep))

            name, releases = self.release_fetcher.fetch_releases(dep.name)

            if name in solved:
                raise SolverException("Dependency: {} is listed multiple times".format(name))

            if not releases:
                if graceful:
                    _LOGGER.info("No releases found for package %r", dep.name)
                else:
                    raise SolverException("No releases found for package {!r}".format(dep.name))

            releases = [release for release in releases if release in dep]
            matching = sorted(releases, key=cmp_to_key(_compare_version_index_url))

            _LOGGER.debug("  matching: %s", matching)

            if all_versions:
                solved[name] = matching
            else:
                if not matching:
                    solved[name] = None
                else:
                    if self._highest_dependency_version:
                        solved[name] = matching[-1]
                    else:
                        solved[name] = matching[0]

        return solved


def get_ecosystem_solver(ecosystem_name, parser_kwargs=None, fetcher_kwargs=None):
    """Get Solver subclass instance for particular ecosystem.

    :param ecosystem_name: name of ecosystem for which solver should be get
    :param parser_kwargs: parser key-value arguments for constructor
    :param fetcher_kwargs: fetcher key-value arguments for constructor
    :return: Solver
    """
    from .python import PythonSolver

    if ecosystem_name.lower() == "pypi":
        source = Source(url="https://pypi.org/simple", warehouse_api_url="https://pypi.org/pypi", warehouse=True)
        return PythonSolver(parser_kwargs, fetcher_kwargs={"source": source})

    raise NotImplementedError("Unknown ecosystem: {}".format(ecosystem_name))
