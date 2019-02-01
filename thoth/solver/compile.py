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

"""Run pip-compile and verify result."""

import tempfile

from piptools.scripts.compile import cli
from click.testing import CliRunner

from thoth.common import cwd

from .exceptions import ThothPipCompileError


def pip_compile(*packages: str):
    """Run pip-compile to pin down packages, also resolve their transitive dependencies."""
    result = None
    packages = "\n".join(packages)

    with tempfile.TemporaryDirectory() as tmp_dirname, cwd(tmp_dirname):
        with open("requirements.in", "w") as requirements_file:
            requirements_file.write(packages)

        runner = CliRunner()

        try:
            result = runner.invoke(cli, ["requirements.in"], catch_exceptions=False)
        except Exception as exc:
            raise ThothPipCompileError(str(exc)) from exc

        if result.exit_code != 0:
            error_msg = (
                f"pip-compile returned non-zero ({result.exit_code:d}) " f"output: {result.output_bytes.decode():s}"
            )
            raise ThothPipCompileError(error_msg)

    return result.output_bytes.decode()
