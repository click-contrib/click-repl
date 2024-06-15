from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import ReplContext


# To store the ReplContext objects generated throughout the Runtime.
_context_stack: list[ReplContext] = []


def _push_context(ctx: ReplContext) -> None:
    """
    Pushes a new REPL context onto the current stack.

    Parameters
    ----------
    ctx
        The :class:`~click_repl.core.ReplContext` object that should be
        added to the REPL context stack.
    """
    _context_stack.append(ctx)


def _pop_context() -> None:
    """Removes the top-level REPL context from the stack."""
    _context_stack.pop()
