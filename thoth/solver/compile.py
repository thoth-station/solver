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
        with open('requirements.in', 'w') as requirements_file:
            requirements_file.write(packages)

        runner = CliRunner()

        try:
            result = runner.invoke(cli, ['requirements.in'], catch_exceptions=False)
        except Exception as exc:
            raise ThothPipCompileError(str(exc)) from exc

        if result.exit_code != 0:
            error_msg = "pip-compile returned non-zero " \
                        "({:d}) exit code: %s".format(result.exit_code, result.output_bytes.decode())
            raise ThothPipCompileError(error_msg)

    return result.output_bytes.decode()
