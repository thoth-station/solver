"""Classes for resolving dependencies as specified in each ecosystem."""

import logging
from pip.req.req_file import parse_requirements
from xmlrpc.client import ServerProxy
from subprocess import check_output
from tempfile import NamedTemporaryFile

from .base import Dependency
from .base import DependencyParser
from .base import ReleasesFetcher
from .base import Solver

_LOGGER = logging.getLogger(__name__)


class PypiReleasesFetcher(ReleasesFetcher):
    """Releases fetcher for Pypi."""

    _DEFAULT_FETCH_URL = 'https://pypi.python.org/pypi'

    def __init__(self, fetch_url=None):
        """Initialize instance."""
        super().__init__()
        self._rpc = ServerProxy(fetch_url or self._DEFAULT_FETCH_URL)

    def _search_package_name(self, package):
        """Case insensitive search.

        :param package: str, Name of the package
        :return:
        """
        def find_pypi_pkg(package):
            packages = self._rpc.search({'name': package})
            if packages:
                exact_match = [p['name']
                               for p in packages
                               if p['name'].lower() == package.lower()]
                if exact_match:
                    return exact_match.pop()
        res = find_pypi_pkg(package)
        if res is None and '-' in package:
            # this is soooo annoying; you can `pip3 install argon2-cffi and it installs
            #  argon2_cffi (underscore instead of dash), but searching through XMLRPC
            #  API doesn't find it... so we try to search for underscore variant
            #  if the dash variant isn't found
            res = find_pypi_pkg(package.replace('-', '_'))
        if res:
            return res

        raise ValueError("Package {} not found".format(package))

    def fetch_releases(self, package):
        """Fetch package releases versions.

        XML-RPC API Documentation: https://wiki.python.org/moin/PyPIXmlRpc
        Signature: package_releases(package_name, show_hidden=False)
        """
        if not package:
            raise ValueError("package")

        releases = self._rpc.package_releases(package, True)
        if not releases:
            # try again with swapped case of first character
            releases = self._rpc.package_releases(package[0].swapcase() + package[1:], True)
        if not releases:
            # if nothing was found then do case-insensitive search
            return self.fetch_releases(self._search_package_name(package))

        return package.lower(), releases


class PypiDependencyParser(DependencyParser):
    """Pypi Dependency parsing."""

    @staticmethod
    def parse_python(spec):
        """Parse PyPI specification of a single dependency.

        :param spec: str, for example "Django>=1.5,<1.8"
        :return: [Django [[('>=', '1.5'), ('<', '1.8')]]]
        """
        def _extract_op_version(spec):
            # https://www.python.org/dev/peps/pep-0440/#compatible-release
            if spec.operator == '~=':
                version = spec.version.split('.')
                if len(version) in {2, 3, 4}:
                    if len(version) in {3, 4}:
                        del version[-1]  # will increase the last but one in next line
                    version[-1] = str(int(version[-1]) + 1)
                else:
                    raise ValueError('%r must not be used with %r' % (spec.operator, spec.version))
                return [('>=', spec.version), ('<', '.'.join(version))]
            # Trailing .* is permitted per
            # https://www.python.org/dev/peps/pep-0440/#version-matching
            elif spec.operator == '==' and spec.version.endswith('.*'):
                try:
                    result = check_output(['/usr/bin/semver-ranger', spec.version],
                                          universal_newlines=True).strip()
                    gte, lt = result.split()
                    return [('>=', gte.lstrip('>=')), ('<', lt.lstrip('<'))]
                except ValueError:
                    _LOGGER.info("couldn't resolve ==%s", spec.version)
                    return spec.operator, spec.version
            # https://www.python.org/dev/peps/pep-0440/#arbitrary-equality
            # Use of this operator is heavily discouraged, so just convert it to 'Version matching'
            elif spec.operator == '===':
                return '==', spec.version
            else:
                return spec.operator, spec.version

        def _get_pip_spec(requirements):
            """There's no `specs` field In Pip 8+, take info from `specifier` field."""
            if hasattr(requirements, 'specs'):
                return requirements.specs
            elif hasattr(requirements, 'specifier'):
                specs = [_extract_op_version(spec) for spec in requirements.specifier]
                if len(specs) == 0:
                    # TODO: I'm not sure with this one
                    # we should probably return None instead and let pip deal with this
                    specs = [('>=', '0.0.0')]
                return specs

        # create a temporary file and store the spec there since
        # `parse_requirements` requires a file
        with NamedTemporaryFile(mode='w+', suffix='pysolve') as f:
            f.write(spec)
            f.flush()
            parsed = parse_requirements(f.name, session=f.name)
            dependency = [Dependency(x.name, _get_pip_spec(x.req)) for x in parsed].pop()

        return dependency

    def parse(self, specs):
        """Parse specs."""
        return [self.parse_python(s) for s in specs]

    @staticmethod
    def compose(deps):
        """Compose deps."""
        return DependencyParser.compose_sep(deps, ',')

    @staticmethod
    def restrict_versions(deps):
        """Not implemented."""
        return deps  # TODO


class PypiSolver(Solver):
    """Pypi dependencies solver."""

    def __init__(self, parser_kwargs=None, fetcher_kwargs=None, solver_kwargs=None):
        """Initialize instance."""
        super().__init__(PypiDependencyParser(**(parser_kwargs or {})),
                         PypiReleasesFetcher(**(fetcher_kwargs or {})),
                         **(solver_kwargs or {}))
