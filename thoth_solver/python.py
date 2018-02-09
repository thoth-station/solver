"""Dependency requirements solving for Python ecosystem."""

from contextlib import contextmanager
import datetime
import json
import logging
import os
import typing

import delegator

from collections import deque

from .utils import tempdir
from .solvers import get_ecosystem_solver
from .solvers import PypiDependencyParser

_LOGGER = logging.getLogger(__name__)
_PYPI_SOLVER = get_ecosystem_solver('pypi')


class _CommandError(RuntimeError):
    """Exception raised on error when calling commands."""

    def __init__(self, *args, command: delegator.Command):
        super().__init__(self, *args)
        self.command = command

    @property
    def stdout(self):
        return self.command.out

    @property
    def stderr(self):
        return self.command.err

    @property
    def return_code(self):
        return self.command.return_code

    @property
    def timeout(self):
        return self.command.timeout

    def as_dict(self):
        return {
            'stdout': self.stdout,
            'stderr': self.stderr,
            'return_code': self.return_code,
            'command': self.command.cmd,
            'timeout': self.timeout,
            'message': str(self)
        }


def _get_virtualenv_details(venv_path: str) -> dict:
    """Get information about created virtual environment where packages are installed."""
    result = {}

    venv_info = _pipdeptree(os.path.join(venv_path, 'bin', 'pipdeptree'))

    for entry in venv_info:
        package_name = entry['package']['package_name']
        package_version = entry['package']['installed_version']
        if package_name in result:
            _LOGGER.error("Multiple versions of same package %r installed - version %r and %r,"
                          "maybe bug in pipdeptree?", package_name, package_version, list(result[package_name].keys()))

        result[package_name] = {}
        result[package_name][package_version] = _filter_package_dependencies(entry)

    return result


@contextmanager
def _virtualenv(python_version: int):
    """Create a virtualenv in a temporary directory. Once context is left, all files inside virtualenv are discarded."""
    with tempdir() as tempdir_path:
        _LOGGER.debug("Creating virtual environment in %r", tempdir_path)
        command = delegator.run('virtualenv -p {} venv'.format('python3' if python_version == 3 else 'python2'),
                                timeout=datetime.timedelta(minutes=15).total_seconds())
        _LOGGER.debug(command.out)
        if command.return_code != 0:
            raise _CommandError("Failed to create virtualenv: {}".format(command.err), command=command)

        # Install pipdeptree into virtual environment so we can use it. Do not specify any version, if pipdeptree is a
        # dependency of some requirement, it can be locked - reuse that version.
        command = delegator.run('{} install pipdeptree'.format(os.path.join(tempdir_path, 'venv', 'bin', 'pip')))
        _LOGGER.debug("Installing pipdeptree into virtual environment: %s", command.out)
        if command.return_code != 0:
            raise _CommandError("Failed to install pipdeptree into virtual environment: {}".format(command.err),
                                command=command)

        # It's ok not to clear after yield, directory tree will be erased by tempdir()
        yield os.path.join(tempdir_path, 'venv', 'bin'), _get_virtualenv_details(os.path.join(tempdir_path, 'venv'))


def _install_requirement(pip_bin: str, package: str, version: str, index_url: str=None) -> None:
    """Install requirements specified using suggested pip binary."""
    cmd = '{} install --force-reinstall --no-cache-dir --no-deps '.format(pip_bin)
    if index_url:
        cmd += '--index-url "{}" '.format(index_url)
    cmd += '{}=={}'.format(package, version)

    _LOGGER.debug("Installing requirement via pip: %r" % cmd)
    command = delegator.run(cmd)
    _LOGGER.debug("Output of pip during installation: %s", command.out)
    if command.return_code != 0:
        raise _CommandError("Failed to install requirement via pip: {}".format(command.err), command=command)


def _pipdeptree(pipdeptree_bin: str, package_name: str=None) -> typing.Optional[dict]:
    """Get pip dependency tree by executing pipdeptree tool."""
    cmd = '{} --json'.format(pipdeptree_bin)

    _LOGGER.debug("Obtaining pip dependency tree using: %r", cmd)
    command = delegator.run(cmd)
    if command.return_code != 0:
        raise _CommandError("Failed to call pipdeptree to retrieve package information: {}".format(command.err),
                            command=command)

    output = json.loads(command.out)

    if not package_name:
        return output

    for entry in output:
        # In some versions pipdeptree does not work with --packages flag, do the logic on out own.
        if entry['package']['package_name'] == package_name:
            return entry

    # The given package was not found.
    return None


def _get_dependency_specification(dep_spec: typing.List[tuple]) -> str:
    """Get string representation of dependency specification as provided by PypiDependencyParser."""
    return ",".join(dep_range[0] + dep_range[1] for dep_range in dep_spec)


def _filter_package_dependencies(package_info: dict) -> dict:
    dependencies = {}

    for dependency in package_info['dependencies']:
        dependencies[dependency['package_name']] = dependency['required_version']

    return dependencies


def _resolve_versions(package_name: str, version_spec: str) -> typing.List[str]:
    resolved_versions = _PYPI_SOLVER.solve([package_name + (version_spec or '')], all_versions=True)
    assert len(resolved_versions.keys()) == 1,\
        "Resolution of one package version ended with multiple packages."
    return list(resolved_versions.values())[0]


def resolve(requirements: typing.List[str], index_url: str=None, python_version: int=3,
            exclude_packages: set=None) -> dict:
    """Common code abstracted for tree() and and resolve() functions."""
    assert python_version in (2, 3), "Unknown Python version"

    packages = {}
    errors = {}
    unresolved = []
    exclude_packages = exclude_packages or {}
    queue = deque()

    for requirement in requirements:
        dependency = PypiDependencyParser.parse_python(requirement)
        if dependency.name in exclude_packages:
            continue

        version_spec = _get_dependency_specification(dependency.spec)
        resolved_versions = _resolve_versions(dependency.name, version_spec)
        if not resolved_versions:
            _LOGGER.error("No versions were resolved for dependency %r in version %r", dependency.name, version_spec)
            unresolved.append(requirement)
        else:
            for version in resolved_versions:
                queue.append((dependency.name, version))

    with _virtualenv(python_version) as (venv_bin, venv_details):
        while queue:
            package_name, package_version = queue.pop()

            try:
                _install_requirement(
                    os.path.join(venv_bin, 'pip'),
                    package_name,
                    package_version,
                    index_url
                )
            except _CommandError as exc:
                _LOGGER.error("Failed to install requirement %r in version %r", package_name, package_version)
                if package_name not in errors or package_version not in errors[package_name]:
                    if package_name not in errors:
                        errors[package_name] = {}
                    errors[package_name][package_version] = {
                        'type': 'command_error',
                        'details': exc.as_dict()
                    }
                continue

            try:
                package_info = _pipdeptree(os.path.join(venv_bin, 'pipdeptree'), package_name)
            except _CommandError as exc:
                if package_name not in errors:
                    errors[package_name] = {}
                errors[package_name][package_version] = {
                    'type': 'command_error',
                    'details': exc.as_dict()
                }
                continue

            if package_info is None:
                # FIXME: pipdeptree looks for packages only inside site-packages
                # We should be fine with this approach for now, but there will be a need to fix
                # this in future probably.
                if package_name not in errors:
                    errors[package_name] = {}
                errors[package_name][package_version] = {
                    'type': 'not_site_package',
                    'details': {
                        'message': 'Failed to get information about installed package, probably not site package'
                    }
                }
                continue

            if package_info['package']['installed_version'] != package_version:
                # FIXME: this can resolve in infinite loop if there will be some cyclic dependency
                _LOGGER.error("Requested to install version %r of package %r, but installed "
                              "version is %r, error is not fatal",
                              package_version, package_name, package_info['package']['installed_version'])
                package_version = package_info['package']['installed_version']

            if package_info['package']['package_name'] != package_name:
                _LOGGER.error("Requested to install package %r, but installed package name is %r, error is not fatal",
                              package_name, package_info['package']['package_name'])
                package_name = package_info['package']['package_name']

            if package_name not in packages:
                packages[package_name] = {}

            dependencies = _filter_package_dependencies(package_info)

            for dependency_name, dependency_range in dependencies.items():
                resolved_versions = _resolve_versions(dependency_name, dependency_range)

                for version in resolved_versions:
                    # Did we check this package already?
                    if (dependency_name not in packages or version not in packages[dependency_name]) \
                            and (dependency_name not in errors or version not in errors[dependency_name]):
                        queue.append((dependency_name, version))

            packages[package_name][package_version] = dependencies

            # We could uninstall the package here to save some disk space.

    return {
        'tree': packages,
        'errors': errors,
        'unresolved': unresolved,
        'virtualenv': venv_details
    }
