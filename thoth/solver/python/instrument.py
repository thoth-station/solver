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

"""Functions which are executed inside virtual environment.

These functions are used to gather characteristics about installed packages which are analyzed.

All the functions are executed in a virtualenv - they should print information to stdout, if any error occurs
they should print error messages to stderr and call sys.exit with non-zero value. All necessary functions should
be either from standard virtualenv packages or from standard library to remove any dependency inference.
"""

import inspect
import sys
import shlex
import logging

from thoth.analyzer import run_command

from .._typing import MYPY_CHECK_RUNNING

if MYPY_CHECK_RUNNING:  # pragma: no cover
    from typing import Dict, Any, Optional, Callable, Union


_LOGGER = logging.getLogger(__name__)


def _find_distribution_name(package_name):  # type: (str) -> None
    """Find the given distribution based on package name and print out distribution's project name.

    For example, `backports-weakref' has distribution's project nmae `backports.weakref'. This is also
    applicable to all namespace'd packages - we need to find the actual name. based on distribution discovery.
    """
    import sys
    import pkg_resources
    from pkg_resources._vendor.packaging.utils import canonicalize_name

    for path in sys.path:
        for distribution in pkg_resources.find_distributions(path):
            if canonicalize_name(distribution.project_name) == canonicalize_name(package_name):
                print(distribution.project_name, end="")
                sys.exit(0)

    print("No matching distribution found for ", package_name, file=sys.stderr, end="")
    sys.exit(1)


def _get_importlib_metadata_metadata(package_name):  # type: (str) -> None
    """"Retrieve all the metadata for the given package."""
    import sys

    sys.path = sys.path[::-1]

    import importlib_metadata
    import json

    result = dict(importlib_metadata.metadata(package_name).items())

    # As metadata are encoded as email.message, it's not possible to implicitly expose information about which keys
    # keep multiple values and which are single-value. Let's explicitly maintain a list for metadata keys that
    # are arrays:
    #    https://packaging.python.org/specifications/core-metadata
    keys = frozenset(
        (
            "Platform",
            "Supported-Platform",
            "Classifier",
            "Provides-Dist",
            "Requires-Dist",
            "Requires-External",
            "Project-URL",
            "Provides-Extra",
        )
    )
    for key in keys:
        value = importlib_metadata.metadata(package_name).get_all(key)
        if value:
            # Override the previous one (single value) with array.
            result[key] = value

    print(json.dumps(result))
    sys.exit(0)


def _get_importlib_metadata_version(package_name):  # type: (str) -> None
    """"Retrieve version based for the given package."""
    import sys

    sys.path = sys.path[::-1]

    import importlib_metadata

    print(importlib_metadata.version(package_name), end="")
    sys.exit(0)


def _get_importlib_metadata_requires(package_name):  # type: (str) -> None
    """"Retrieve requires based for the given package."""
    import sys

    sys.path = sys.path[::-1]

    import importlib_metadata
    import json

    print(json.dumps(importlib_metadata.requires(package_name)))
    sys.exit(0)


def _get_importlib_metadata_entry_points(package_name):  # type: (str) -> None
    """Retrieve information about entry-points for the given package."""
    import sys

    sys.path = sys.path[::-1]

    import importlib_metadata
    import json

    entry_points = importlib_metadata.distribution(package_name).entry_points
    print(json.dumps([{"name": ep.name, "value": ep.value, "group": ep.group} for ep in entry_points]))
    sys.exit(0)


def _get_importlib_metadata_files(package_name):  # type: (str) -> None
    """Retrieve information about files present for the given package."""
    import sys

    sys.path = sys.path[::-1]

    from importlib_metadata import files
    import json

    print(
        json.dumps(
            [{"hash": f.hash.__dict__ if f.hash else None, "size": f.size, "path": str(f)} for f in files(package_name)]
        )
    )
    sys.exit(0)


def execute_env_function(
    python_bin,  # type: str
    function,  # type: Callable[[Any], None]
    *,
    env=None,  # type: Optional[Dict[str, str]]
    raise_on_error=True,  # type: bool
    is_json=False,  # type: bool
    **function_arguments,  # type: Any
):  # type: (...) -> Optional[Union[str, Dict[str, Any]]]
    """Execute the given function in Python interpreter."""
    kwargs = ""
    for argument, value in function_arguments.items():
        if kwargs:
            kwargs += ","

        kwargs += argument + '="' + value + '"'

    function_source = inspect.getsource(function)
    cmd = python_bin + " -c " + (shlex.quote(function_source + "\n\n" + function.__name__ + "(" + kwargs + ")"))
    _LOGGER.debug("Executing the following command in Python interpreter (env: %r): %r", env, cmd)
    res = run_command(cmd, env=env, is_json=is_json, raise_on_error=False)

    _LOGGER.debug("stdout during command execution: %s", res.stdout)
    _LOGGER.debug("stderr during command execution: %s", res.stderr)

    if raise_on_error and res.return_code != 0:
        raise ValueError("Failed to successfully execute function in Python interpreter: {}".format(res.stderr))

    if res.return_code == 0:
        stdout = res.stdout  # type: Union[str, Dict[str, Any]]
        return stdout

    _LOGGER.error("Failed to successfully execute function in Python interpreter: %r", res.stderr)
    return None


def get_package_metadata(python_bin, package_name):
    # type: (str, str) -> Dict[str, Any]
    """Get metadata information from the installed package."""
    # A simple trick when running importlib_metadata - importlib_metadata is present as
    # a dependency of this package, but it is not installed in the created virtual environment.
    # Inject the current path to the created environment. Note however,
    # we need to make sure importlib_metadata correctly handles metadata of packages which are dependencies of this
    # package - each function executed in the virtual environment should reverse sys.path to give precedence
    # in importing packages from virtual environment, and then, import from the environment where solver runs in.
    return {
        "metadata": execute_env_function(
            python_bin,
            _get_importlib_metadata_metadata,
            env={"PYTHONPATH": ":".join(sys.path)},
            is_json=True,
            package_name=package_name,
        ),
        "requires": execute_env_function(
            python_bin,
            _get_importlib_metadata_requires,
            env={"PYTHONPATH": ":".join(sys.path)},
            is_json=True,
            package_name=package_name,
        ),
        "entry_points": execute_env_function(
            python_bin,
            _get_importlib_metadata_entry_points,
            env={"PYTHONPATH": ":".join(sys.path)},
            is_json=True,
            package_name=package_name,
        ),
        "files": execute_env_function(
            python_bin,
            _get_importlib_metadata_files,
            env={"PYTHONPATH": ":".join(sys.path)},
            is_json=True,
            package_name=package_name,
        ),
        "version": execute_env_function(
            python_bin,
            _get_importlib_metadata_version,
            env={"PYTHONPATH": ":".join(sys.path)},
            is_json=False,
            package_name=package_name,
        ),
    }


def find_distribution_name(python_bin, package_name):  # type: (str, str) -> str
    """Find distribution name based on the package name."""
    result = str(execute_env_function(python_bin, _find_distribution_name, package_name=package_name))
    return result
