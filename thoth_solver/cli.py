#!/usr/bin/env python3
"""Thoth-solver CLI."""

import datetime
import json
import platform
import sys
import typing

import click
import logging
import requests
from rainbow_logging_handler import RainbowLoggingHandler

from thoth_solver import __version__ as thoth_solver_version
from thoth_solver.python import resolve as resolve_pypi
from thoth_solver.python import tree as tree_pypi

_LOG = logging.getLogger(__name__)


def _setup_logging(verbose, no_color):
    """Set up Python logging based on verbosity level.

    :param verbose: verbosity level
    :param no_color: do not use colorized output
    """
    level = logging.INFO if not verbose else logging.DEBUG
    logger = logging.getLogger()
    logger.setLevel(level)

    if not no_color:
        formatter = logging.Formatter("%(process)d: [%(asctime)s] %(name)s %(funcName)s:%(lineno)d: %(message)s")
        # setup RainbowLoggingHandler
        handler = RainbowLoggingHandler(sys.stderr)
        handler.setFormatter(formatter)
        logger.addHandler(handler)


def _print_version(ctx, _, value):
    """Print solver version and exit."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(thoth_solver_version)
    ctx.exit()


def _print_command_result(result: typing.Union[dict, list], output: str = None,
                          pretty: bool = True, metadata: dict = None) -> None:
    """Print or submit results, nicely if requested."""
    metadata = metadata or {}
    metadata['version'] = thoth_solver_version
    metadata['datetime'] = datetime.datetime.now().isoformat()
    metadata['hostname'] = platform.node()
    metadata['analyzer'] = __name__.split('.')[0]

    content = {
        'result': result,
        'metadata': metadata
    }

    if isinstance(output, str) and output.startswith(('http://', 'https://')):
        _LOG.info("Submitting results to %r", output)
        requests.post(output, json=content)
        return

    kwargs = {}
    if pretty:
        kwargs['sort_keys'] = True
        kwargs['separators'] = (',', ': ')
        kwargs['indent'] = 2

    content = json.dumps(content, **kwargs)
    if output is None or output == '-':
        sys.stdout.write(content)
    else:
        _LOG.info("Writing results to %r", output)
        with open(output, 'w') as output_file:
            output_file.write(content)


@click.group()
@click.pass_context
@click.option('-v', '--verbose', is_flag=True,
              help="Be verbose about what's going on.")
@click.option('--version', is_flag=True, is_eager=True, callback=_print_version, expose_value=False,
              help="Print solver version and exit.")
@click.option('--no-color', is_flag=True,
              help="Suppress colorized logging output.")
def cli(ctx=None, verbose=0, no_color=True):
    """Thoth solver command line interface."""
    if ctx:
        ctx.auto_envvar_prefix = 'THOTH_SOLVER'
    _setup_logging(verbose, no_color)


@cli.command()
@click.option('--requirements', '-r', default='-', type=click.File(), show_default=True,
              help="Requirements file to be solved.")
@click.option('--ignore-version-ranges', '-i', is_flag=True,
              help="Resolve to all version instead of the ones that match version ranges.")
@click.option('--index', '-i', type=str,
              help="Python index to be used when resolving version ranges.")
@click.option('--python-version', '-p', type=click.Choice(['2', '3']), default='3', show_default=True,
              help="Set Python interpreter version to be used.")
@click.option('--tree-only', '-t', is_flag=True,
              help="Do not create stacks, print dependency tree instead with specified versions.")
@click.option('--exclude-packages', '-e', type=str, metavar='PKG1,PKG2',
              help="A comma separated list of packages that should be excluded from the final listing.")
def pypi(requirements, ignore_version_ranges=False, index=None, python_version=3,
         tree_only=False, exclude_packages=None):
    """Manipulate with dependency requirements using PyPI."""
    requirements = [requirement.strip() for requirement in requirements.read().split('\n') if requirement]
    metadata = locals()

    if tree_only:
        result = tree_pypi(
            requirements,
            ignore_version_ranges=ignore_version_ranges,
            index_url=index,
            python_version=int(python_version),
            exclude_packages=set(map(str.strip, (exclude_packages or '').split(',')))
        )
    else:
        result = resolve_pypi(
            requirements,
            ignore_version_ranges=ignore_version_ranges,
            index_url=index,
            python_version=int(python_version),
            exclude_packages=set(map(str.strip, (exclude_packages or '').split(',')))
        )

    _print_command_result(result, metadata=metadata)


if __name__ == '__main__':
    cli()
