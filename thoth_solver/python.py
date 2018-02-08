"""Dependency requirements solving for Python ecosystem."""

from contextlib import contextmanager
import datetime
import json
import logging
import os

import delegator

from .utils import tempdir
from .solvers import get_ecosystem_solver
from .solvers import PypiDependencyParser

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


def get_pipdeptree(pipdeptree_bin, package_names, exclude_packages):
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

        result_dependencies = []
        entry['package'].pop('installed_version')
        for dependency in entry['dependencies']:
            if dependency['package_name'] in exclude_packages:
                continue

            dependency.pop('installed_version')
            result_dependencies.append(dependency)
            if dependency['key'] == 'pipdeptree':
                pipdeptree_required = True

        entry['dependencies'] = result_dependencies
        if entry['package']['key'] == 'pipdeptree':
            # We will append pipdeptree if it is actually a dependency of some package or if required explicitly.
            pipdeptree_entry = entry
            continue

        if entry['package']['package_name'] not in exclude_packages:
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
            dependency['resolved_versions'] = list(solver.solve([requirement], all_versions=True).values())[0]


def get_all_locked_stacks(dependency_tree, requirements_text=[], index_url=None, exclude_packages=None):
    """Get all stacks with full locked dependencies."""
    exclude_packages = exclude_packages or {}

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
        if package_name in exclude_packages:
            continue

        if package_name not in packages:
            dep_spec = ''
            # If the given package was explicitly specified with the given version range,
            # respect it in the final output.
            for requirement in requirements_text:
                if package_name == requirement[0]:
                    dep_spec = requirement[1]
                    break
            packages[package_name] = solver.solve([package_name + dep_spec], all_versions=True).pop(package_name)

    all_requirements = []
    for package_name, versions in packages.items():
        all_package_requirements = []
        for version in versions:
            all_package_requirements.append("{}=={}\n".format(package_name, version))
        all_requirements.append(all_package_requirements)

    return {package_name: versions for package_name, versions in packages.items()}


def get_dependency_specification(dep_spec):
    """Get string representation of dependency specification as provided by PypiDependencyParser."""
    return ",".join(dep_range[0] + dep_range[1] for dep_range in dep_spec)


def _do_work(requirements, ignore_version_ranges=False, index_url=None, python_version=3,
             tree_only=False, exclude_packages=None):
    """Common code abstracted for tree() and and resolve() functions."""
    assert python_version in (2, 3), "Unknown Python version"
    exclude_packages = exclude_packages or {}
    requirements = [PypiDependencyParser.parse_python(requirement) for requirement in requirements]
    requirements_text = [(dep.name, get_dependency_specification(dep.spec)) for dep in requirements]

    with virtualenv(python_version) as venv_bin:
        install_requirements(os.path.join(venv_bin, 'pip'), (req[0] + req[1] for req in requirements_text), index_url)
        dependency_tree = get_pipdeptree(os.path.join(venv_bin, 'pipdeptree'), [req.name for req in requirements],
                                         exclude_packages)
        resolve_package_versions(dependency_tree, ignore_version_ranges, index_url)

        if tree_only:
            return dependency_tree

        _LOGGER.debug("Resolved package versions: %s", json.dumps(dependency_tree))
        return get_all_locked_stacks(dependency_tree, requirements_text, index_url)


def tree(requirements, ignore_version_ranges=False, index_url=None, python_version=3, exclude_packages=None):
    """Get tree-like structure of dependencies specified in requirements."""
    return _do_work(
        requirements,
        ignore_version_ranges=ignore_version_ranges,
        index_url=index_url,
        python_version=python_version,
        tree_only=True,
        exclude_packages=exclude_packages or {},
    )


def resolve(requirements, ignore_version_ranges=False, index_url=None, python_version=3, exclude_packages=None):
    """Get all stacks that are possible for the given requirements specification."""
    return _do_work(
        requirements,
        ignore_version_ranges=ignore_version_ranges,
        index_url=index_url,
        python_version=python_version,
        tree_only=False,
        exclude_packages=exclude_packages or {},
    )
