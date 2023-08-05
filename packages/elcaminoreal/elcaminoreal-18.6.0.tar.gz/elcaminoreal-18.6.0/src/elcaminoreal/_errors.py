"""
Capture argument parsing errors
"""
import contextlib

import caparg


@contextlib.contextmanager
def errors_to(filep):
    """
    A context manager for command-line parsing errors.

    It will catch caparg parsing errors, and redirect
    the output into the given file descriptor.

    Suggested usage:

    .. code::

        with errors_to(sys.stderr):
            COMMANDS.run(....)
    """
    try:
        yield
    except caparg.ParseError as exc:
        filep.write(exc.message)
