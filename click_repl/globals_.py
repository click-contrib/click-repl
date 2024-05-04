from __future__ import annotations

import sys
from typing import TYPE_CHECKING, NoReturn

from ._ctx_stack import _context_stack

if TYPE_CHECKING:
    from .core import ReplContext


ISATTY = sys.stdin.isatty()


def get_current_repl_ctx(silent: bool = False) -> ReplContext | NoReturn | None:
    """
    Retrieves the current click-repl context.

    This function provides a way to access the context from anywhere
    in the code. This function serves as a more implicit alternative to the
    :func:`~click.core.pass_context` decorator.

    Parameters
    ----------
    silent
        If set to :obj:`True`, the function returns :obj:`None` if no context
        is available. The default behavior is to raise a :exc:`~RuntimeError`.

    Returns
    -------
    :class:`~click_repl.core.ReplContext` | None
        REPL context object if available, or :obj:`None` if ``silent`` is :obj:`True`.

    Raises
    ------
    RuntimeError
        If there's no context object in the stack and ``silent`` is :obj:`False`.
    """

    try:
        return _context_stack[-1]
    except IndexError:
        if not silent:
            raise RuntimeError("There is no active click-repl context.")

    return None
