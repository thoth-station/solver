"""Exception hierarchy used in thoth-solver."""


class ThothSolverExceptionBase(Exception):
    """Top level solver exception in thoth-solver hierarchy."""


class ThothPipCompileError(ThothSolverExceptionBase):
    """Exception raised by pip-compile."""
