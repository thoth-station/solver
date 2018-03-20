#!/usr/bin/env python3
"""Thoth-solver CLI."""

import sys

import click
import logging
from rainbow_logging_handler import RainbowLoggingHandler

from thoth.analyzer import print_command_result

from thoth.solver import __title__ as analyzer_name
from thoth.solver import __version__ as analyzer_version
from thoth.solver.python import resolve as resolve_pypi

_LOG = logging.getLogger(__name__)


def _setup_logging(verbose, no_color):
    """Set up Python logging based on verbosity level.

    :param verbose: verbosity level
    :param no_color: do not use colorized output
    """
    # TODO: move this logic to thoth-analyzer or thoth-common

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
    click.echo(analyzer_version)
    ctx.exit()


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


@cli.command()
@click.pass_context
@click.option('--requirements', '-r', type=str, envvar='THOTH_SOLVER_PACKAGES', required=True,
              help="Requirements to be solved.")
@click.option('--index', '-i', type=str,
              help="Python index to be used when resolving version ranges.")
@click.option('--output', '-o', type=str, envvar='THOTH_SOLVER_OUTPUT', default='-',
              help="Output file or remote API to print results to, in case of URL a POST request is issued.")
@click.option('--no-pretty', '-P', is_flag=True,
              help="Do not print results nicely.")
@click.option('--exclude-packages', '-e', type=str, metavar='PKG1,PKG2',
              help="A comma separated list of packages that should be excluded from the final listing.")
@click.option('--no-transitive', '-T', is_flag=True, envvar='THOTH_SOLVER_NO_TRANSITIVE',
              help="Do not check transitive dependencies, run only on provided requirements.")
def pypi(click_ctx, requirements, index=None, python_version=3, exclude_packages=None, output=None,
         no_transitive=True, no_pretty=False):
    """Manipulate with dependency requirements using PyPI."""
    requirements = [requirement.strip() for requirement in requirements.split('\n') if requirement]

    if not requirements:
        _LOG.error("No requirements specified, exiting")
        sys.exit(1)

    result = resolve_pypi(
        requirements,
        index_url=index,
        python_version=int(python_version),
        transitive=not no_transitive,
        exclude_packages=set(map(str.strip, (exclude_packages or '').split(',')))
    )

    print_command_result(click_ctx, result, analyzer=analyzer_name, analyzer_version=analyzer_version,
                         output=output or '-', pretty=not no_pretty)


if __name__ == '__main__':
    cli()
