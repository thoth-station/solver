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

"""Dependency requirements solving for Python ecosystem."""

from collections import deque
from contextlib import contextmanager
import logging
import os
from shlex import quote
from urllib.parse import urlparse

from packaging.requirements import Requirement
from packaging.markers import default_environment
from packaging.markers import Variable
from packaging.markers import Op
from packaging.markers import Value
from packaging.utils import canonicalize_name
from thoth.analyzer import CommandError
from thoth.analyzer import run_command
from thoth.python import Source
from thoth.python.exceptions import NotFound

from .python_solver import PythonDependencyParser
from .python_solver import PythonSolver
from .instrument import get_package_metadata
from .instrument import find_distribution_name

from .._typing import MYPY_CHECK_RUNNING

if MYPY_CHECK_RUNNING:  # pragma: no cover
    from typing import List, Tuple, Dict, Generator, Optional, Any, Set, Deque, Union


_LOGGER = logging.getLogger(__name__)


def get_environment_packages(python_bin):  # type: (str) -> List[Dict[str, str]]
    """Get information about packages in environment where packages get installed."""
    cmd = "{} -m pip freeze".format(python_bin)
    output = run_command(cmd, is_json=False).stdout.splitlines()

    result = []
    for line in output:
        package_name, package_version = line.split("==", maxsplit=1)
        result.append({"package_name": package_name, "package_version": package_version})

    return result


@contextmanager
def _install_requirement(python_bin, package, version=None, index_url=None, clean=True):
    # type: (str, str, Optional[str], Optional[str], bool) -> Generator[None, None, None]
    """Install requirements specified using suggested pip binary."""
    previous_version = _pipdeptree(python_bin, package)

    try:
        cmd = "{} -m pip install --force-reinstall --no-cache-dir --no-deps {}".format(python_bin, quote(package))
        if version:
            cmd += "=={}".format(quote(version))
        if index_url:
            cmd += ' --index-url "{}" '.format(quote(index_url))
            # Supply trusted host by default so we do not get errors - it safe to
            # do it here as package indexes are managed by Thoth.
            trusted_host = urlparse(index_url).netloc
            cmd += " --trusted-host {}".format(trusted_host)

        _LOGGER.debug("Installing requirement %r in version %r", package, version)
        result = run_command(cmd)
        _LOGGER.debug("Log during installation:\nstdout: %s\nstderr:%s", result.stdout, result.stderr)
        yield
    finally:
        if clean:
            _LOGGER.debug("Removing installed package %r", package)
            cmd = "{} -m pip uninstall --yes {}".format(python_bin, quote(package))
            result = run_command(cmd, raise_on_error=False)

            if result.return_code != 0:
                _LOGGER.warning(
                    "Failed to restore previous environment by removing package %r (installed version %r), "
                    "the error is not fatal but can affect future actions: %s",
                    package,
                    version,
                    result.stderr,
                )

            _LOGGER.debug(
                "Restoring previous environment setup after installation of %r (%s)", package, previous_version
            )
            if previous_version:
                cmd = "{} -m pip install --force-reinstall --no-cache-dir --no-deps {}=={}".format(
                    python_bin, quote(package), quote(previous_version["package"]["installed_version"])
                )
                _LOGGER.debug("Running %r", cmd)
                result = run_command(cmd, raise_on_error=False)

                if result.return_code != 0:
                    _LOGGER.warning(
                        "Failed to restore previous environment for package %r (installed version %r), "
                        ", the error is not fatal but can affect future actions (previous version: %r): %s",
                        package,
                        version,
                        previous_version,
                        result.stderr,
                    )


def _pipdeptree(python_bin, package_name=None, warn=False):
    # type: (str, Optional[str], bool) -> Any
    """Get pip dependency tree by executing pipdeptree tool."""
    cmd = "{} -m pipdeptree --json".format(python_bin)

    _LOGGER.debug("Obtaining pip dependency tree using: %r", cmd)
    output = run_command(cmd, is_json=True).stdout  # type: List[Dict[str, Any]]

    if not package_name:
        return output

    for entry in output:  # type: Dict[str, Any]
        # In some versions pipdeptree does not work with --packages flag, do the logic on out own.
        # TODO: we should probably do difference of reference this output and original environment
        if entry["package"]["key"].lower() == package_name.lower():
            return entry

    # The given package was not found.
    if warn:
        _LOGGER.warning("Package %r was not found in pipdeptree output %r", package_name, output)
    return None


def _marker_reduction(marker, extra):  # type: ignore
    """Convert internal packaging marker representation to interpretation which can be evaluated.

    As markers also depend on `extra' which will cause issues when evaluating marker in the solver
    environment, let's substitute `extra' marker with a condition which evaluates always to true.
    """
    if isinstance(marker, str):
        return marker

    if isinstance(marker, list):
        result_markers = []
        for nested_marker in marker:
            reduced_marker = _marker_reduction(nested_marker, extra)  # type: ignore
            result_markers.append(reduced_marker)

        return result_markers

    if marker[0].value != "extra":
        return marker

    extra.add(str(marker[2]))
    # A special case to handle extras in markers - substitute extra with a marker which always evaluates to true:
    return Variable("python_version"), Op(">="), Value("0.0")


def parse_requirement_str(requirement_str):
    # type: (str) -> Dict[str, Any]
    """Parse a string representation of marker."""
    # Some notes on this implementation can be found at: https://github.com/pypa/packaging/issues/211
    requirement = Requirement(requirement_str)

    evaluation_result = None
    evaluation_error = None
    extra = set()  # type: Set[str]
    marker_evaluated_str = None
    marker_str = str(requirement.marker) if requirement.marker else None
    if requirement.marker:
        # We perform a copy of marker specification during the traversal so that we
        # do not evaluate "extra" marker - according to PEP-508, this behavior
        # raises an error if the interpreting environment does not explicitly
        # define them. As we are aggregating "generic" data and extra is
        # user-defined on the actual resolution, we exclude this extra marker
        # here.
        markers_copy = []
        for marker in requirement.marker._markers:
            marker_copy = _marker_reduction(marker, extra)  # type: ignore
            markers_copy.append(marker_copy)

        try:
            requirement.marker._markers = markers_copy
            evaluation_result = requirement.marker.evaluate()
            marker_evaluated_str = str(requirement.marker)
        except Exception as exc:
            _LOGGER.exception("Failed to evaluate marker {}".format(requirement.marker))
            evaluation_error = str(exc)
    else:
        evaluation_result = True

    return {
        "package_name": requirement.name,
        "normalized_package_name": canonicalize_name(requirement.name),
        "specifier": str(requirement.specifier) if requirement.specifier else None,
        "resolved_versions": [],
        "extras": list(requirement.extras),
        "extra": list(extra),
        "marker": marker_str,
        "marker_evaluated": marker_evaluated_str,
        "marker_evaluation_result": evaluation_result,
        "marker_evaluation_error": evaluation_error,
    }


def extract_metadata(metadata, index_url):
    # type: (Dict[str, Any], str) -> Dict[str, Any]
    """Extract and enhance information from metadata."""
    result = {
        "dependencies": [],
        "package_name": metadata["metadata"].get("Name"),
        "package_version": metadata["metadata"].get("Version"),
        "index_url": index_url,
        "importlib_metadata": metadata,
    }

    for requirement_str in metadata.get("requires") or []:
        result["dependencies"].append(parse_requirement_str(requirement_str))

    return result


def _resolve_versions(solver, source, package_name, version_spec):
    # type: (PythonSolver, Source, str, str) -> List[str]
    try:
        resolved_versions = solver.solve([package_name + (version_spec or "")])
    except NotFound:
        _LOGGER.info(
            "No versions were resovled for %r with version specification %r for package index %r",
            package_name,
            version_spec,
            source.url,
        )
        return []
    except Exception:  # pylint: disable=broad-except
        _LOGGER.exception("Failed to resolve versions for %r with version spec %r", package_name, version_spec)
        return []

    assert len(resolved_versions.keys()) == 1, "Resolution of one package version ended with multiple packages."

    result = []
    for item in list(resolved_versions.values())[0]:
        result.append(item[0])  # We remove information about indexes.

    return result


def _fill_hashes(source, package_name, package_version, extracted_metadata):
    # type: (Source, str, str, Dict[str, Any]) -> None
    extracted_metadata["sha256"] = []
    try:
        package_hashes = source.get_package_hashes(package_name, package_version)
    except NotFound:
        # Some older packages have different version on PyPI (considering simple API) than the ones
        # stated in metadata.
        package_hashes = source.get_package_hashes(package_name, extracted_metadata["version"])
    for item in package_hashes:
        extracted_metadata["sha256"].append(item["sha256"])


def _do_resolve_index(python_bin, solver, all_solvers, requirements, exclude_packages, transitive):
    # type: (str, PythonSolver, List[PythonSolver], List[str], Optional[Set[str]], bool) -> Dict[str, Any]
    """Perform resolution of requirements against the given solver."""
    index_url = solver.releases_fetcher.index_url
    source = solver.releases_fetcher.source

    packages_seen = set()
    packages = []
    errors = []
    unresolved = []
    unparsed = []
    exclude_packages = exclude_packages or set()
    queue = deque()  # type: Deque[Tuple[str, str]]

    for requirement in requirements:
        _LOGGER.debug("Parsing requirement %r", requirement)
        try:
            dependency = PythonDependencyParser.parse_python(requirement)
        except Exception as exc:
            _LOGGER.warning("Failed to parse requirement %r: %s", requirement, str(exc))
            unparsed.append({"requirement": requirement, "details": str(exc)})
            continue

        if dependency.name in exclude_packages:
            continue

        version_spec = str(dependency.specifier)
        _LOGGER.info(
            "Resolving package %r with version specifier %r from %r",
            dependency.name,
            version_spec,
            source.url
        )
        resolved_versions = _resolve_versions(solver, source, dependency.name, version_spec)
        if not resolved_versions:
            _LOGGER.warning("No versions were resolved for dependency %r in version %r", dependency.name, version_spec)
            unresolved.append(
                {
                    "package_name": dependency.name,
                    "version_spec": version_spec,
                    "index_url": index_url,
                    "is_provided": dependency.name in source.get_packages(),
                }
            )
        else:
            for version in resolved_versions:
                _LOGGER.info("Adding package %r in version %r for solving", dependency.name, version)
                entry = (dependency.name, version)
                packages_seen.add(entry)
                queue.append(entry)

    while queue:
        package_name, package_version = queue.pop()
        _LOGGER.info("Using index %r to discover package %r in version %r", index_url, package_name, package_version)
        try:
            with _install_requirement(python_bin, package_name, package_version, index_url):
                # Translate to distribution name - e.g. thoth-solver is actually distribution thoth.solver.
                package_name = find_distribution_name(python_bin, package_name)
                package_metadata = get_package_metadata(python_bin, package_name)
                extracted_metadata = extract_metadata(package_metadata, index_url)
        except (CommandError, Exception) as exc:
            _LOGGER.debug(
                "There was an error during package %r in version %r discovery from %r: %s",
                package_name,
                package_version,
                index_url,
                exc,
            )
            if not isinstance(exc, CommandError):
                # Report any error happening during metadata aggregation so we know if there is a programming error.
                # An example reported message:
                #  https://github.com/thoth-station/solver/issues/342
                _LOGGER.exception("An exception occurred during package metadata gathering")
                details = {"message": str(exc)}
            else:
                details = exc.to_dict()

            errors.append(
                {
                    "package_name": package_name,
                    "index_url": index_url,
                    "package_version": package_version,
                    "type": "command_error",
                    "details": details,
                    "is_provided": source.provides_package_version(package_name, package_version),
                }
            )
            continue

        packages.append(extracted_metadata)
        if package_version != extracted_metadata["package_version"]:
            _LOGGER.warning(
                "Requested to install package %r in version %r but installed version is %r",
                package_name,
                package_version,
                extracted_metadata["package_version"],
            )

        extracted_metadata["package_version_requested"] = package_version
        _fill_hashes(source, package_name, package_version, extracted_metadata)

        for dependency in extracted_metadata["dependencies"]:
            dependency_name, dependency_specifier = dependency["normalized_package_name"], dependency["specifier"]

            for dep_solver in all_solvers:
                _LOGGER.info(
                    "Resolving dependency versions for %r with range %r from %r",
                    dependency_name,
                    dependency_specifier,
                    dep_solver.releases_fetcher.index_url,
                )
                resolved_versions = _resolve_versions(
                    dep_solver, dep_solver.releases_fetcher.source, dependency_name, dependency_specifier or ""
                )
                _LOGGER.debug(
                    "Resolved versions for package %r with range specifier %r: %s",
                    dependency_name,
                    dependency_specifier,
                    resolved_versions,
                )
                dependency["resolved_versions"].append(
                    {"versions": resolved_versions, "index": dep_solver.releases_fetcher.index_url}
                )

                if not transitive:
                    continue

                for version in resolved_versions:
                    # Did we check this package already - do not check indexes, we manually insert them.
                    seen_entry = (dependency_name, version)
                    if seen_entry not in packages_seen:
                        _LOGGER.debug(
                            "Adding package %r in version %r for next resolution round", dependency_name, version
                        )
                        packages_seen.add(seen_entry)
                        queue.append((dependency_name, version))

    return {"tree": packages, "errors": errors, "unparsed": unparsed, "unresolved": unresolved}


def resolve(requirements, index_urls, python_version, exclude_packages, transitive, virtualenv):
    # type: (List[str], List[str], int, Optional[Set[str]], bool, Optional[str]) -> Dict[str, Any]
    """Resolve given requirements for the given Python version."""
    assert python_version in (2, 3), "Unknown Python version"

    python_bin = "python3" if python_version == 3 else "python2"
    if not virtualenv:
        run_command("virtualenv -p " + python_bin + " venv")
        python_bin = os.path.join("venv", "bin", python_bin)
        run_command("{} -m pip install pipdeptree".format(python_bin))
    else:
        python_bin = os.path.join(virtualenv, "bin", python_bin)

    environment_packages = get_environment_packages(python_bin)

    result = {
        "tree": [],
        "errors": [],
        "unparsed": [],
        "unresolved": [],
        "environment": default_environment(),
        "environment_packages": environment_packages,
    }

    all_solvers = []
    for index_url in index_urls:
        source = Source(index_url)
        from .python_solver import PythonReleasesFetcher

        all_solvers.append(
            PythonSolver(
                dependency_parser=PythonDependencyParser(), releases_fetcher=PythonReleasesFetcher(source=source)
            )
        )

    for solver in all_solvers:
        solver_result = _do_resolve_index(
            python_bin=python_bin,
            solver=solver,
            all_solvers=all_solvers,
            requirements=requirements,
            exclude_packages=exclude_packages,
            transitive=transitive,
        )

        result["tree"].extend(solver_result["tree"])
        result["errors"].extend(solver_result["errors"])
        result["unparsed"].extend(solver_result["unparsed"])
        result["unresolved"].extend(solver_result["unresolved"])

    return result
