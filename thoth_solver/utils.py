"""Various cross-library utilities."""

import os
import tempfile
import shutil

from contextlib import contextmanager


@contextmanager
def cwd(target):
    """Manage cwd in a pushd/popd fashion."""
    curdir = os.getcwd()
    os.chdir(target)
    try:
        yield curdir
    finally:
        os.chdir(curdir)


@contextmanager
def tempdir() -> str:
    """Create a temporary directory and temporary cd into it with context manager."""
    dir_path = tempfile.mkdtemp()

    try:
        with cwd(dir_path):
            yield dir_path
    finally:
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
