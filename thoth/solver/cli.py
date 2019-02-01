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

"""Thoth-solver CLI."""

import sys

import click
import logging

from thoth.analyzer import print_command_result
from thoth.common import init_logging

from thoth.solver import __title__ as analyzer_name
from thoth.solver import __version__ as analyzer_version
from thoth.solver.python import resolve as resolve_python

init_logging()

_LOG = logging.getLogger(__name__)


def _print_version(ctx, _, value):
    """Print solver version and exit."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(analyzer_version)
    ctx.exit()


@click.group()
@click.pass_context
@click.option("-v", "--verbose", is_flag=True, envvar="THOTH_SOLVER_DEBUG", help="Be verbose about what's going on.")
@click.option(
    "--version",
    is_flag=True,
    is_eager=True,
    callback=_print_version,
    expose_value=False,
    help="Print solver version and exit.",
)
def cli(ctx=None, verbose=0):
    """Thoth solver command line interface."""
    if ctx:
        ctx.auto_envvar_prefix = "THOTH_SOLVER"

    if verbose:
        _LOG.setLevel(logging.DEBUG)

    _LOG.debug("Debug mode is on")


@cli.command()
@click.pass_context
@click.option(
    "--requirements", "-r", type=str, envvar="THOTH_SOLVER_PACKAGES", required=True, help="Requirements to be solved."
)
@click.option(
    "--index",
    "-i",
    type=str,
    envvar="THOTH_SOLVER_INDEXES",
    show_default=True,
    default="https://pypi.org/simple",
    help="A comma separated list of Python indexes to be used when resolving version ranges.",
)
@click.option(
    "--output",
    "-o",
    type=str,
    envvar="THOTH_SOLVER_OUTPUT",
    default="-",
    help="Output file or remote API to print results to, in case of URL a POST request is issued.",
)
@click.option("--no-pretty", "-P", is_flag=True, help="Do not print results nicely.")
@click.option(
    "--exclude-packages",
    "-e",
    type=str,
    metavar="PKG1,PKG2",
    help="A comma separated list of packages that should be excluded from the final listing.",
)
@click.option(
    "--no-transitive",
    "-T",
    is_flag=True,
    envvar="THOTH_SOLVER_NO_TRANSITIVE",
    help="Do not check transitive dependencies, run only on provided requirements.",
)
@click.option(
    "--subgraph-check-api",
    type=str,
    envvar="THOTH_SOLVER_SUBGRAPH_CHECK_API",
    help="An API to be queried to retrieve information whether the given subgraph should be resolved.",
)
def pypi(
    click_ctx,
    requirements,
    index=None,
    python_version=3,
    exclude_packages=None,
    output=None,
    subgraph_check_api=None,
    no_transitive=True,
    no_pretty=False,
):
    """Manipulate with dependency requirements using PyPI."""
    requirements = [requirement.strip() for requirement in requirements.split("\\n") if requirement]

    if not requirements:
        _LOG.error("No requirements specified, exiting")
        sys.exit(1)

    if not subgraph_check_api:
        _LOG.info(
            "No subgraph check API provided, no queries will be done for dependency subgraphs that should be avoided"
        )  # Ignore PycodestyleBear (E501)

    result = resolve_python(
        requirements,
        index_urls=index.split(",") if index else ("https://pypi.org/simple",),
        python_version=int(python_version),
        transitive=not no_transitive,
        exclude_packages=set(map(str.strip, (exclude_packages or "").split(","))),
        subgraph_check_api=subgraph_check_api,
    )

    print_command_result(
        click_ctx,
        result,
        analyzer=analyzer_name,
        analyzer_version=analyzer_version,
        output=output or "-",
        pretty=not no_pretty,
    )


if __name__ == "__main__":
    cli()
