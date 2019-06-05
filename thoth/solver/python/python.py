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
import sys
from collections import deque
from contextlib import contextmanager
import logging
import typing
from shlex import quote
from urllib.parse import urlparse

import http
import requests
from thoth.analyzer import CommandError
from thoth.analyzer import run_command
from thoth.python import Source
from thoth.python.exceptions import NotFound

from .python_solver import PythonDependencyParser
from .python_solver import PythonSolver

_LOGGER = logging.getLogger(__name__)


def _create_entry(entry: dict, source: Source = None) -> dict:
    """Filter and normalize the output of pipdeptree entry."""
    entry["package_name"] = entry["package"].pop("package_name")
    entry["package_version"] = entry["package"].pop("installed_version")

    if source:
        entry["index_url"] = source.url
        entry["sha256"] = []
        for item in source.get_package_hashes(entry["package_name"], entry["package_version"]):
            entry["sha256"].append(item["sha256"])

    entry.pop("package")
    for dependency in entry["dependencies"]:
        dependency.pop("key", None)
        dependency.pop("installed_version", None)

    return entry


def _get_environment_details(python_bin: str) -> list:
    """Get information about packages in environment where packages get installed."""
    cmd = "{} -m pipdeptree --json".format(python_bin)
    output = run_command(cmd, is_json=True).stdout
    return [_create_entry(entry) for entry in output]


def _should_resolve_subgraph(subgraph_check_api: str, package_name: str, package_version: str, index_url: str) -> bool:
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
    for i in range(3):
        response = requests.get(
            subgraph_check_api,
            params={
                "package_name": package_name,
                "package_version": package_version,
                "index_url": index_url,
                "solver_name": solver_name,
            },
        )

        if response.status_code in (200, 208):
            break

        _LOGGER.debug(
            "Invalid response from subgraph check API %r, retrying (status code: %d): %r",
            subgraph_check_api,
            response.status_code,
            response.text
        )
    else:
        response.raise_for_status()

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
        solver_name
    )


@contextmanager
def _install_requirement(
    python_bin: str, package: str, version: str = None, index_url: str = None, clean: bool = True
) -> None:
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


def _pipdeptree(python_bin, package_name: str = None, warn: bool = False) -> typing.Optional[dict]:
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
                entry = (dependency.name, version)
                packages_seen.add(entry)
                queue.append(entry)

    while queue:
        package_name, package_version = queue.pop()
        _LOGGER.info("Using index %r to discover package %r in version %r", index_url, package_name, package_version)
        try:
            with _install_requirement(python_bin, package_name, package_version, index_url):
                package_info = _pipdeptree(python_bin, package_name, warn=True)
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
                    "version": package_version,
                    "type": "command_error",
                    "details": exc.to_dict(),
                }
            )
            continue

        if package_info is None:
            errors.append(
                {
                    "package_name": package_name,
                    "index": index_url,
                    "version": package_version,
                    "type": "not_site_package",
                    "details": {
                        "message": "Failed to get information about installed package, probably not site package"
                    },
                }
            )
            continue

        if package_info["package"]["installed_version"] != package_version:
            _LOGGER.warning(
                "Requested to install version %r of package %r, but installed version is %r, error is not fatal",
                package_version,
                package_name,
                package_info["package"]["installed_version"],
            )

        if package_info["package"]["package_name"] != package_name:
            _LOGGER.warning(
                "Requested to install package %r, but installed package name is %r, error is not fatal",
                package_name,
                package_info["package"]["package_name"],
            )

        entry = _create_entry(package_info, source)
        packages.append(entry)

        for dependency in entry["dependencies"]:
            dependency_name, dependency_range = dependency["package_name"], dependency["required_version"]
            dependency["resolved_versions"] = []

            for dep_solver in all_solvers:
                _LOGGER.info(
                    "Resolving dependency versions for %r with range %r from %r",
                    dependency_name,
                    dependency_range,
                    dep_solver.release_fetcher.index_url,
                )
                resolved_versions = _resolve_versions(
                    dep_solver, dep_solver.release_fetcher.source, dependency_name, dependency_range
                )
                _LOGGER.debug(
                    "Resolved versions for package %r with range specifier %r: %s",
                    dependency_name,
                    dependency_range,
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
                            and _should_resolve_subgraph(subgraph_check_api, dependency_name, version, index_url)
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
        _LOGGER.error("The check against subgraph API cannot be done if no transitive dependencies are resolved")
        sys.exit(2)

    python_bin = "python3" if python_version == 3 else "python2"
    run_command("virtualenv -p python3 venv")
    python_bin = "venv/bin/" + python_bin

    run_command("{} -m pip install pipdeptree".format(python_bin))
    environment_details = _get_environment_details(python_bin)

    result = {"tree": [], "errors": [], "unparsed": [], "unresolved": [], "environment": environment_details}

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
