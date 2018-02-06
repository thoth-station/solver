"""Dependency requirements solving for Python ecosystem."""

from contextlib import contextmanager
import datetime
import itertools
import json
import logging
import os

import delegator

from .utils import tempdir
from .solvers import get_ecosystem_solver


_LOGGER = logging.getLogger(__name__)


@contextmanager
def virtualenv(python_version):
    """Create a virtualenv in a temporary directory. Once context is left, all files inside virtualenv are discarded."""
    with tempdir() as tempdir_path:
        _LOGGER.debug("Creating virtual environment in %r", tempdir_path)
        command = delegator.run('virtualenv -p {} venv'.format('python3' if python_version == 3 else 'python2'),
                                timeout=datetime.timedelta(minutes=15).total_seconds())
        _LOGGER.debug(command.out)
        if command.return_code != 0:
            raise RuntimeError("Failed to create virtualenv: {}".format(command.err))

        # It's ok not to clear after yield, directory tree will be erased by tempdir()
        yield os.path.join(tempdir_path, 'venv', 'bin')


def install_requirements(pip_bin, requirements, index_url=None):
    """Install requirements specified using suggested pip binary."""
    # TODO: hashes will not work
    cmd = '{} install --no-cache-dir '.format(pip_bin)
    if index_url:
        cmd += '--index-url "{}"'.format(index_url)
    cmd += ' ' + ' '.join(requirements)

    _LOGGER.debug("Installing requirements via pip: %r" % cmd)
    command = delegator.run(cmd)
    _LOGGER.debug("Output of pip during installation: %s", command.out)
    if command.return_code != 0:
        raise RuntimeError("Failed to install requirements via pip: {}".format(command.err))

    # Install pipdeptree into virtual environment so we can use it. Do not specify any version, if pipdeptree is a
    # dependency of some requirement, it can be locked - reuse that version.
    command = delegator.run('{} install pipdeptree'.format(pip_bin))
    _LOGGER.debug("Installing pipdeptree into virtual environment: %s", command.out)
    if command.return_code != 0:
        raise RuntimeError("Failed to install pipdeptree into virtual environment: {}".format(command.err))


def get_package_names(requirements):
    """Get package names from a requirement specification."""
    # Note that the order is significant - '===' should precede '=='
    version_specifiers = ('===', '==', '<=', '>=', '!=', '~=', '>', '<')
    package_names = []

    for requirement in requirements:
        for version_specifier in version_specifiers:
            package_name = requirement.split(version_specifier)
            if len(package_name) == 2:
                package_names.append(package_name[0])
                break
        else:
            # There was no version specifier, but package name only.
            package_names.append(requirement)

    return package_names


def get_pipdeptree(pipdeptree_bin, package_names):
    """Get pip dependency tree by executing pipdeptree tool."""
    cmd = '{} --json --packages {}'.format(pipdeptree_bin, ','.join(package_names))
    _LOGGER.debug("Obtaining pip dependency tree using: %r", cmd)
    command = delegator.run(cmd)
    if command.return_code != 0:
        raise RuntimeError("Failed to call pipdeptree to retrieve package information: {}".format(command.err))

    output = json.loads(command.out)

    # At the end of the day, we simply don't care what versions were installed.
    result = []
    pipdeptree_entry = None
    pipdeptree_required = 'pipdeptree' in package_names
    for entry in output:

        entry['package'].pop('installed_version')
        for dependency in entry['dependencies']:
            dependency.pop('installed_version')
            if dependency['key'] == 'pipdeptree':
                pipdeptree_required = True

        if entry['package']['key'] == 'pipdeptree':
            # We will append pipdeptree if it is actually a dependency of some package or if required explicitly.
            pipdeptree_entry = entry
            continue

        # TODO: excluded packages
        result.append(entry)

    if pipdeptree_required:
        result.append(pipdeptree_entry)

    return result


def resolve_package_versions(dependency_tree, ignore_version_ranges, index_url):
    """Resolve packages to all possible versions that match version range criteria."""
    solver = get_ecosystem_solver('pypi', fetcher_kwargs={'fetch_url': index_url})
    for entry in dependency_tree:
        for dependency in entry['dependencies']:
            requirement = dependency['package_name']
            if dependency['required_version'] is not None and not ignore_version_ranges:
                requirement += dependency['required_version']

            # TODO: add possibility to specify version range explicitly
            dependency['resolved_versions'] = solver.solve([requirement], all_versions=True).\
                pop(dependency['package_name'])


def get_all_locked_stacks(dependency_tree, index_url=None):
    """Get all stacks with full locked dependencies."""
    packages = {}
    for entry in dependency_tree:
        for dependency in entry['dependencies']:
            if dependency['key'] in packages:
                possible_versions = []
                for version in packages[dependency['key']]:
                    if version in dependency['resolved_versions']:
                        possible_versions.append(version)
                packages[dependency['key']] = possible_versions

            else:
                packages[dependency['key']] = dependency['resolved_versions']

    # Now traverse top-level dependencies.
    solver = get_ecosystem_solver('pypi', fetcher_kwargs={'fetch_url': index_url})
    for entry in dependency_tree:
        package_name = entry['package']['key']
        if package_name not in packages:
            # TODO: excluded packages
            packages[package_name] = solver.solve([package_name], all_versions=True).pop(package_name)

    all_requirements = []
    for package_name, versions in packages.items():
        all_package_requirements = []
        for version in versions:
            all_package_requirements.append("{}=={}\n".format(package_name, version))
        all_requirements.append(all_package_requirements)

    return itertools.product(*all_requirements)


def _do_work(requirements, ignore_version_ranges=False, index_url=None, python_version=3, tree_only=False):
    """Common code abstracted for tree() and and resolve() functions."""
    assert python_version in (2, 3), "Unknown Python version"

    with virtualenv(python_version) as venv_bin:
        install_requirements(os.path.join(venv_bin, 'pip'), requirements, index_url)
        dependency_tree = get_pipdeptree(os.path.join(venv_bin, 'pipdeptree'), get_package_names(requirements))
        resolve_package_versions(dependency_tree, ignore_version_ranges, index_url)

        if tree_only:
            return dependency_tree

        _LOGGER.debug("Resolved package versions: %s", json.dumps(dependency_tree))
        return list(get_all_locked_stacks(dependency_tree, index_url))


def tree(requirements, ignore_version_ranges=False, index_url=None, python_version=3):
    """Get tree-like structure of dependencies specified in requirements."""
    return _do_work(
        requirements,
        ignore_version_ranges=ignore_version_ranges,
        index_url=index_url,
        python_version=python_version,
        tree_only=True
    )


def resolve(requirements, ignore_version_ranges=False, index_url=None, python_version=3):
    """Get all stacks that are possible for the given requirements specification."""
    return _do_work(
        requirements,
        ignore_version_ranges=ignore_version_ranges,
        index_url=index_url,
        python_version=python_version,
        tree_only=False
    )
