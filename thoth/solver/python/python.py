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

import os
import time
from collections import deque
from contextlib import contextmanager
import logging
import typing
from shlex import quote
from urllib.parse import urlparse

import http
import requests
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

from thoth.solver.python.python_solver import PythonDependencyParser
from thoth.solver.python.python_solver import PythonSolver
from thoth.solver.python.instrument import get_package_metadata
from thoth.solver.python.instrument import find_distribution_name

_LOGGER = logging.getLogger(__name__)


def get_environment_packages(python_bin: str) -> list:
    """Get information about packages in environment where packages get installed."""
    cmd = "{} -m pip freeze".format(python_bin)
    output = run_command(cmd, is_json=False).stdout.splitlines()

    result = []
    for line in output:
        package_name, package_version = line.split("==", maxsplit=1)
        result.append({"package_name": package_name, "package_version": package_version})

    return result


def should_resolve_subgraph(subgraph_check_api: str, package_name: str, package_version: str, index_url: str) -> bool:
    """Ask the given subgraph check API if the given package in the given version should be included in the resolution.

    This subgraph resolving avoidence serves two purposes - we don't need to
    resolve dependency subgraphs that were already analyzed and we also avoid
    analyzing of "core" packages (like setuptools) where not needed as they
    can break installation environment.
    """
    # This variable is expected to be set in deployment to guarantee solver name correctness for subgraph checks.
    solver_name = os.environ["THOTH_SOLVER"]
    _LOGGER.info(
        "Checking if the given dependency subgraph for package %r in version %r from index %r should be resolved by %r",
        package_name,
        package_version,
        index_url,
        solver_name,
    )

    response = None
    for i in range(10):
        try:
            response = requests.get(
                subgraph_check_api,
                params={
                    "package_name": package_name,
                    "package_version": package_version,
                    "index_url": index_url,
                    "solver_name": solver_name,
                },
            )
        except requests.exceptions.ConnectionError as exc:
            _LOGGER.warning("Client got disconnected, retrying: %s", str(exc))
            # Retry after some time.
            time.sleep(1)
            continue

        if response.status_code in (200, 208):
            break

        _LOGGER.warning(
            "Invalid response from subgraph check API %r, retrying (status code: %d): %r",
            subgraph_check_api,
            response.status_code,
            response.text,
        )
        # Retry after some time.
        time.sleep(1)
    else:
        if response:
            response.raise_for_status()

        # We received ConnectionError only exceptions.
        raise requests.exceptions.ConnectionError("Too many connection errors when performing sub-graph checks")

    if response.status_code == http.HTTPStatus.OK:
        return True
    elif response.status_code == http.HTTPStatus.ALREADY_REPORTED:
        # FIXME This is probably not the correct HTTP status code to be used here, but which one should be used?
        return False

    raise ValueError(
        "Unreachable code - subgraph check API responded with unknown HTTP status "
        "code %s for package %r in version %r from index %r, solver %r",
        package_name,
        package_version,
        index_url,
        solver_name,
    )


@contextmanager
def _install_requirement(
    python_bin: str, package: str, version: str = None, index_url: str = None, clean: bool = True
) -> None:
    """Install requirements specified using suggested pip binary."""
    previous_version = pipdeptree(python_bin, package)

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
        run_command(cmd)
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


def pipdeptree(python_bin, package_name: str = None, warn: bool = False) -> typing.Optional[dict]:
    """Get pip dependency tree by executing pipdeptree tool."""
    cmd = "{} -m pipdeptree --json".format(python_bin)

    _LOGGER.debug("Obtaining pip dependency tree using: %r", cmd)
    output = run_command(cmd, is_json=True).stdout

    if not package_name:
        return output

    for entry in output:
        # In some versions pipdeptree does not work with --packages flag, do the logic on out own.
        # TODO: we should probably do difference of reference this output and original environment
        if entry["package"]["key"].lower() == package_name.lower():
            return entry

    # The given package was not found.
    if warn:
        _LOGGER.warning("Package %r was not found in pipdeptree output %r", package_name, output)
    return None


def _marker2json(marker, extras):
    """Convert internal packaging marker representation into a JSON."""
    if isinstance(marker, str):
        return marker, marker

    if isinstance(marker, list):
        result_json = []
        result_markers = []
        for nested_marker in marker:
            marker_json, marker_packaging = _marker2json(nested_marker, extras)
            result_json.append(marker_json)
            result_markers.append(marker_packaging)

        return result_json, result_markers

    if marker[0].value != "extra":
        return {"variable": str(marker[0]), "op": str(marker[1]), "value": str(marker[2])}, marker

    extras.add(str(marker[2]))
    # A special case to handle extras in markers - substitute extra with a marker which always evaluates to true:
    return (
        {"op": ">=", "value": "0.0", "variable": "python_version"},
        (Variable("python_version"), Op(">="), Value("0.0")),
    )


def parse_requirement_str(requirement_str: str):
    """Parse a string representation of marker."""
    # Some notes on this implementation can be found at: https://github.com/pypa/packaging/issues/211
    requirement = Requirement(requirement_str)

    parsed_markers = []

    evaluation_result = None
    evaluation_error = None
    extras = set()
    marker_str = None
    if requirement.marker:
        # We perform a copy of marker specification during the traversal so that we
        # do not evaluate "extra" marker - according to PEP-508, this behavior
        # raises an error if the interpreting environment does not explicitly
        # define them. As we are aggregating "generic" data and extra is
        # user-defined on the actual resolution, we exclude this extra marker
        # here.
        markers_copy = []
        for marker in requirement.marker._markers:
            marker_entry, marker_copy = _marker2json(marker, extras)
            parsed_markers.append(marker_entry)
            markers_copy.append(marker_copy)

        try:
            requirement.marker._markers = markers_copy
            evaluation_result = requirement.marker.evaluate()
            marker_str = str(requirement.marker)
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
        "extras": list(extras),
        "marker": marker_str,
        "marker_evaluation_result": evaluation_result,
        "marker_evaluation_error": evaluation_error,
        "parsed_markers": parsed_markers,
    }


def extract_metadata(metadata: dict) -> dict:
    """Extract and enhance information from metadata."""
    result = {
        "dependencies": [],
        "package_name": metadata["metadata"].get("Name"),
        "package_version": metadata["metadata"].get("Version"),
        "importlib_metadata": metadata,
    }

    for requirement_str in metadata.get("requires") or []:
        result["dependencies"].append(parse_requirement_str(requirement_str))

    return result


def _get_dependency_specification(dep_spec: typing.List[tuple]) -> str:
    """Get string representation of dependency specification as provided by PythonDependencyParser."""
    return ",".join(dep_range[0] + dep_range[1] for dep_range in dep_spec)


def _resolve_versions(solver: PythonSolver, source: Source, package_name: str, version_spec: str) -> typing.List[str]:
    try:
        resolved_versions = solver.solve([package_name + (version_spec or "")], all_versions=True)
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


def _fill_hashes(source: Source, package_name: str, package_version: str, extracted_metadata: dict) -> None:
    extracted_metadata["sha256"] = []
    try:
        package_hashes = source.get_package_hashes(package_name, package_version)
    except NotFound:
        # Some older packages have different version on PyPI (considering simple API) than the ones
        # stated in metadata.
        package_hashes = source.get_package_hashes(package_name, extracted_metadata["package_version"])
    for item in package_hashes:
        extracted_metadata["sha256"].append(item["sha256"])


def _do_resolve_index(
    python_bin: str,
    solver: PythonSolver,
    *,
    all_solvers: typing.List[PythonSolver],
    requirements: typing.List[str],
    exclude_packages: set = None,
    transitive: bool = True,
    subgraph_check_api: str = None,
) -> dict:
    """Perform resolution of requirements against the given solver."""
    index_url = solver.release_fetcher.index_url
    source = solver.release_fetcher.source

    packages_seen = set()
    packages = []
    errors = []
    unresolved = []
    unparsed = []
    exclude_packages = exclude_packages or {}
    queue = deque()

    for requirement in requirements:
        _LOGGER.debug("Parsing requirement %r", requirement)
        try:
            dependency = PythonDependencyParser.parse_python(requirement)
        except Exception as exc:
            unparsed.append({"requirement": requirement, "details": str(exc)})
            continue

        if dependency.name in exclude_packages:
            continue

        version_spec = _get_dependency_specification(dependency.spec)
        resolved_versions = _resolve_versions(solver, source, dependency.name, version_spec)
        if not resolved_versions:
            _LOGGER.warning("No versions were resolved for dependency %r in version %r", dependency.name, version_spec)
            unresolved.append({"package_name": dependency.name, "version_spec": version_spec, "index": index_url})
        else:
            for version in resolved_versions:
                if not subgraph_check_api or (
                    subgraph_check_api
                    and should_resolve_subgraph(subgraph_check_api, dependency.name, version, index_url)
                ):
                    entry = (dependency.name, version)
                    packages_seen.add(entry)
                    queue.append(entry)
                else:
                    _LOGGER.info(
                        "Direct dependency %r in version % from %r was already resolved in one "
                        "of the previous solver runs based on sub-graph check",
                        dependency.name,
                        version,
                        index_url,
                    )

    while queue:
        package_name, package_version = queue.pop()
        _LOGGER.info("Using index %r to discover package %r in version %r", index_url, package_name, package_version)
        try:
            with _install_requirement(python_bin, package_name, package_version, index_url):
                # Translate to distribution name - e.g. thoth-solver is actually distribution thoth.solver.
                package_name = find_distribution_name(python_bin, package_name)
                package_metadata = get_package_metadata(python_bin, package_name)
                extracted_metadata = extract_metadata(package_metadata)
        except CommandError as exc:
            _LOGGER.debug(
                "There was an error during package %r in version %r discovery from %r: %s",
                package_name,
                package_version,
                index_url,
                exc,
            )
            errors.append(
                {
                    "package_name": package_name,
                    "index": index_url,
                    "package_version": package_version,
                    "type": "command_error",
                    "details": exc.to_dict(),
                    "is_provided": source.provides_package_version(package_name, package_version),
                }
            )
            continue

        packages.append(extracted_metadata)
        extracted_metadata["package_version_requested"] = package_version
        _fill_hashes(source, package_name, package_version, extracted_metadata)

        for dependency in extracted_metadata["dependencies"]:
            dependency_name, dependency_specifier = dependency["normalized_package_name"], dependency["specifier"]

            for dep_solver in all_solvers:
                _LOGGER.info(
                    "Resolving dependency versions for %r with range %r from %r",
                    dependency_name,
                    dependency_specifier,
                    dep_solver.release_fetcher.index_url,
                )
                resolved_versions = _resolve_versions(
                    dep_solver, dep_solver.release_fetcher.source, dependency_name, dependency_specifier or ""
                )
                _LOGGER.debug(
                    "Resolved versions for package %r with range specifier %r: %s",
                    dependency_name,
                    dependency_specifier,
                    resolved_versions,
                )
                dependency["resolved_versions"].append(
                    {"versions": resolved_versions, "index": dep_solver.release_fetcher.index_url}
                )

                if not transitive:
                    continue

                for version in resolved_versions:
                    # Did we check this package already - do not check indexes, we manually insert them.
                    seen_entry = (dependency_name, version)
                    if seen_entry not in packages_seen and (
                        not subgraph_check_api
                        or (
                            subgraph_check_api
                            and should_resolve_subgraph(subgraph_check_api, dependency_name, version, index_url)
                        )
                    ):
                        _LOGGER.debug(
                            "Adding package %r in version %r for next resolution round", dependency_name, version
                        )
                        packages_seen.add(seen_entry)
                        queue.append((dependency_name, version))

    return {"tree": packages, "errors": errors, "unparsed": unparsed, "unresolved": unresolved}


def resolve(
    requirements: typing.List[str],
    index_urls: list = None,
    python_version: int = 3,
    exclude_packages: set = None,
    transitive: bool = True,
    subgraph_check_api: str = None,
) -> dict:
    """Resolve given requirements for the given Python version."""
    assert python_version in (2, 3), "Unknown Python version"

    if subgraph_check_api and not transitive:
        _LOGGER.warning(
            "The check against subgraph API cannot be done if no transitive dependencies are "
            "resolved, sub-graph checks are turned off implicitly"
        )
        subgraph_check_api = None

    python_bin = "python3" if python_version == 3 else "python2"
    run_command("virtualenv -p python3 venv")
    python_bin = "venv/bin/" + python_bin

    run_command("{} -m pip install pipdeptree".format(python_bin))
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
        all_solvers.append(PythonSolver(fetcher_kwargs={"source": source}))

    for solver in all_solvers:
        solver_result = _do_resolve_index(
            python_bin=python_bin,
            solver=solver,
            all_solvers=all_solvers,
            requirements=requirements,
            exclude_packages=exclude_packages,
            transitive=transitive,
            subgraph_check_api=subgraph_check_api,
        )

        result["tree"].extend(solver_result["tree"])
        result["errors"].extend(solver_result["errors"])
        result["unparsed"].extend(solver_result["unparsed"])
        result["unresolved"].extend(solver_result["unresolved"])

    return result
