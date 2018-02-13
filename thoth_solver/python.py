"""Dependency requirements solving for Python ecosystem."""

from contextlib import contextmanager
import json
import logging
import typing

import delegator
import hashin

from collections import deque

from .solvers import get_ecosystem_solver
from .solvers import PypiDependencyParser

_LOGGER = logging.getLogger(__name__)
_PYPI_SOLVER = get_ecosystem_solver('pypi')
_HASH_ALGORITHM = 'sha512'


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


def _filter_pipdeptree_entry(entry: dict) ->dict:
    """Filter and normalize the output of pipdeptree entry."""
    entry['package_name'] = entry['package'].pop('package_name')
    entry['installed_version'] = entry['package'].pop('installed_version')
    entry.pop('package')
    for dependency in entry['dependencies']:
        dependency.pop('key', None)
        dependency.pop('installed_version', None)

    return entry


def _get_environment_details(python_bin: str) -> list:
    """Get information about packages in environment where packages get installed."""
    cmd = '{} -m pipdeptree --json'.format(python_bin)

    command = delegator.run(cmd)
    if command.return_code != 0:
        error_msg = "Failed to obtain information about running environment: {}".format(command.err)
        raise _CommandError(error_msg, command=command)

    output = json.loads(command.out)
    return [_filter_pipdeptree_entry(entry) for entry in output]


@contextmanager
def _install_requirement(python_bin: str, package: str, version: str=None, index_url: str=None, clean: bool=True) -> None:
    """Install requirements specified using suggested pip binary."""
    previous_version = _pipdeptree(python_bin, package)

    cmd = '{} -m pip install --force-reinstall --user --no-cache-dir --no-deps {}'.format(python_bin, package)
    if version:
        cmd += '=={}'.format(version)
    if index_url:
        cmd += ' --index-url "{}" '.format(index_url)

    _LOGGER.debug("Installing requirement via pip: %r" % cmd)
    command = delegator.run(cmd)
    _LOGGER.debug("Output of pip during installation: %s", command.out)
    if command.return_code != 0:
        error_msg = "Failed to install requirement via pip: {}".format(command.err)
        _LOGGER.error(error_msg)
        raise _CommandError(error_msg, command=command)

    yield

    if not clean:
        return

    _LOGGER.debug("Restoring previous environment setup after installation of %r", package)

    if previous_version:
        cmd = '{} -m pip install --force-reinstall --user ' \
              '--no-cache-dir --no-deps {}=={}'.format(python_bin,
                                                       package,
                                                       previous_version['package']['installed_version'])
        _LOGGER.debug("Installing previous version %r of package %r", previous_version['package']['installed_version'])
        command = delegator.run(cmd)

        if command.return_code != 0:
            _LOGGER.error("Failed to restore previous environment for package %r (installed version %r, "
                          "previous version %r), the error not fatal but can affect future actions",
                          package, version, previous_version['package']['installed_version'])
            return
    else:
        _LOGGER.debug("Removing installed package %r", package)
        cmd = '{} -m pip uninstall --yes {}'.format(python_bin, package)
        command = delegator.run(cmd)

        if command.return_code != 0:
            _LOGGER.error("Failed to restore previous environment by removing package %r (installed version %r), "
                          "the error not fatal but can affect future actions", package, version)
            return


def _pipdeptree(python_bin, package_name: str=None) -> typing.Optional[dict]:
    """Get pip dependency tree by executing pipdeptree tool."""
    cmd = '{} -m pipdeptree --json --user'.format(python_bin)

    _LOGGER.debug("Obtaining pip dependency tree using: %r", cmd)
    command = delegator.run(cmd)
    if command.return_code != 0:
        error_msg = "Failed to call pipdeptree to retrieve package information: {}".format(command.err)
        raise _CommandError(error_msg, command=command)

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
            exclude_packages: set=None, transitive: bool=True) -> dict:
    """Common code abstracted for tree() and and resolve() functions."""
    assert python_version in (2, 3), "Unknown Python version"

    python_bin = 'python3' if python_version == 3 else 'python2'
    packages_seen = set()
    packages = []
    errors = []
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
                entry = (dependency.name, version)
                packages_seen.add(entry)
                queue.append(entry)

    environment_details = _get_environment_details(python_bin)

    while queue:
        package_name, package_version = queue.pop()

        try:
            with _install_requirement(python_bin, package_name, package_version, index_url):
                try:
                    package_info = _pipdeptree(python_bin, package_name)
                except _CommandError as exc:
                    errors.append({
                        'package': package_name,
                        'version': package_version,
                        'type': 'command_error',
                        'details': exc.as_dict()
                    })
                    continue
        except _CommandError as exc:
            errors.append({
                'package_name': package_name,
                'version': package_version,
                'type': 'command_error',
                'details': exc.as_dict()
            })
            continue

        if package_info is None:
            errors.append({
                'package_name': package_name,
                'version': package_version,
                'type': 'not_site_package',
                'details': {
                    'message': 'Failed to get information about installed package, probably not site package'
                }
            })
            continue

        if package_info['package']['installed_version'] != package_version:
            _LOGGER.error("Requested to install version %r of package %r, but installed "
                          "version is %r, error is not fatal",
                          package_version, package_name, package_info['package']['installed_version'])

        if package_info['package']['package_name'] != package_name:
            _LOGGER.error("Requested to install package %r, but installed package name is %r, error is not fatal",
                          package_name, package_info['package']['package_name'])

        hashes = None
        try:
            # TODO: we should check the hash of the downloaded artifact via `pip hash` and install it afterwards
            hashes = hashin.get_package_hashes(package_name, version=package_version, algorithm=_HASH_ALGORITHM)
        except Exception as exc:
            _LOGGER.error("Failed to obtain hashes for %r in version %r: %s", package_name, package_version, str(exc))

        entry = _filter_pipdeptree_entry(package_info)
        entry['hashes'] = hashes
        entry['hash_type'] = _HASH_ALGORITHM
        packages.append(entry)

        if not transitive:
            continue

        for dependency in package_info['dependencies']:
            dependency_name, dependency_range = dependency['package_name'], dependency['required_version']
            resolved_versions = _resolve_versions(dependency_name, dependency_range)

            for version in resolved_versions:
                # Did we check this package already?
                entry = (dependency_name, version)
                if entry not in packages_seen:
                    packages_seen.add(entry)
                    queue.append(entry)

    return {
        'tree': packages,
        'errors': errors,
        'unresolved': unresolved,
        'environment': environment_details
    }
