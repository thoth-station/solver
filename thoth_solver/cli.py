#!/usr/bin/env python3
"""Thoth-solver CLI."""

import datetime
import json
import os
import platform
import sys
import typing

import click
import distro
import logging
import requests
from rainbow_logging_handler import RainbowLoggingHandler

from thoth_solver import __version__ as thoth_solver_version
from thoth_solver.python import resolve as resolve_pypi

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
    metadata['analyzer'] = __name__.split('.')[0]
    metadata['analyzer_version'] = thoth_solver_version
    metadata['datetime'] = datetime.datetime.now().isoformat()
    metadata['hostname'] = platform.node()
    metadata['distribution'] = distro.info()
    metadata['python'] = {
        'major': sys.version_info.major,
        'minor': sys.version_info.minor,
        'micro': sys.version_info.micro,
        'releaselevel': sys.version_info.releaselevel,
        'serial': sys.version_info.serial,
        'api_version': sys.api_version,
        'implementation_name': sys.implementation.name
    }

    content = {
        'result': result,
        'metadata': metadata
    }

    if isinstance(output, str) and output.startswith(('http://', 'https://')):
        _LOG.info("Submitting results to %r", output)
        response = requests.post(output, json=content)
        response.raise_for_status()
        _LOG.info(response.text)
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
@click.option('-v', '--verbose', is_flag=True, envvar='THOTH_SOLVER_DEBUG',
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


# TODO: transitive?
@cli.command()
@click.option('--requirements', '-r', type=click.File(), default=None,
              help="Requirements file to be solved.")
@click.option('--index', '-i', type=str,
              help="Python index to be used when resolving version ranges.")
@click.option('--output', '-o', type=str, envvar='THOTH_SOLVER_OUTPUT', default='-',
              help="Output file or remote API to print results to, in case of URL a POST request is issued.")
@click.option('--no-pretty', '-P', is_flag=True,
              help="Do not print results nicely.")
@click.option('--python-version', '-p', type=click.Choice(['2', '3']), default='3', show_default=True,
              help="Set Python interpreter version to be used.")
@click.option('--exclude-packages', '-e', type=str, metavar='PKG1,PKG2',
              help="A comma separated list of packages that should be excluded from the final listing.")
@click.option('--no-transitive', '-T', is_flag=True, envvar='THOTH_SOLVER_TRANSITIVE',
              help="Do not check transitive dependencies, run only on provided requirements.")
def pypi(requirements, index=None, python_version=3, exclude_packages=None, output=None,
         no_transitive=True, no_pretty=False):
    """Manipulate with dependency requirements using PyPI."""
    if requirements is None:
        requirements = [requirement.strip() for requirement in
                        os.getenv('THOTH_SOLVER_PACKAGES', "").split('\\n') if requirement]
    else:
        requirements = [requirement.strip() for requirement in requirements.read().split('\n') if requirement]

    if not requirements:
        _LOG.error("No requirements specified via command line, no requirements available "
                   "in THOTH_SOLVER_PACKAGES environment variable")
        sys.exit(1)

    arguments = locals()
    result = resolve_pypi(
        requirements,
        index_url=index,
        python_version=int(python_version),
        transitive=not no_transitive,
        exclude_packages=set(map(str.strip, (exclude_packages or '').split(',')))
    )

    _print_command_result(result, output=output or '-', pretty=not no_pretty, metadata={'arguments': arguments})


if __name__ == '__main__':
    cli()
