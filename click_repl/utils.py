from __future__ import annotations

import os
import shlex
import typing as t
from collections import defaultdict
from typing import Callable, Generator, Iterator, NoReturn, Sequence

import click
from typing_extensions import TypeAlias

from .exceptions import CommandLineParserError, ExitReplException

T = t.TypeVar("T")
InternalCommandCallback: TypeAlias = Callable[[], None]


__all__ = [
    "_execute_internal_and_sys_cmds",
    "_exit_internal",
    "_get_registered_target",
    "_help_internal",
    "_resolve_context",
    "_register_internal_command",
    "dispatch_repl_commands",
    "handle_internal_commands",
    "split_arg_string",
    "exit",
]


def _resolve_context(args: list[str], ctx: click.Context) -> click.Context:
    """Produce the context hierarchy starting with the command and
    traversing the complete arguments. This only follows the commands,
    it doesn't trigger input prompts or callbacks.

    :param args: List of complete args before the incomplete value.
    :param cli_ctx: `click.Context` object of the CLI group
    """

    while args:
        command = ctx.command

        if isinstance(command, click.MultiCommand):
            if not command.chain:
                name, cmd, args = command.resolve_command(ctx, args)

                if cmd is None:
                    return ctx

                ctx = cmd.make_context(name, args, parent=ctx, resilient_parsing=True)
                args = ctx.protected_args + ctx.args
            else:
                while args:
                    name, cmd, args = command.resolve_command(ctx, args)

                    if cmd is None:
                        return ctx

                    sub_ctx = cmd.make_context(
                        name,
                        args,
                        parent=ctx,
                        allow_extra_args=True,
                        allow_interspersed_args=False,
                        resilient_parsing=True,
                    )
                    args = sub_ctx.args

                ctx = sub_ctx
                args = [*sub_ctx.protected_args, *sub_ctx.args]
        else:
            break

    return ctx


_internal_commands: dict[str, tuple[InternalCommandCallback, str | None]] = {}


def split_arg_string(string: str, posix: bool = True) -> list[str]:
    """Split an argument string as with :func:`shlex.split`, but don't
    fail if the string is incomplete. Ignores a missing closing quote or
    incomplete escape sequence and uses the partial token as-is.
    .. code-block:: python
        split_arg_string("example 'my file")
        ["example", "my file"]
        split_arg_string("example my\\")
        ["example", "my"]
    :param string: String to split.
    """

    lex = shlex.shlex(string, posix=posix)
    lex.whitespace_split = True
    lex.commenters = ""
    out = []

    try:
        for token in lex:
            out.append(token)
    except ValueError:
        # Raised when end-of-string is reached in an invalid state. Use
        # the partial token as-is. The quote or escape character is in
        # lex.state, not lex.token.
        out.append(lex.token)

    return out


def _register_internal_command(
    names: str | Sequence[str] | Generator[str, None, None] | Iterator[str],
    target: InternalCommandCallback,
    description: str | None = None,
) -> None:
    if not hasattr(target, "__call__"):
        raise ValueError("Internal command must be a callable")

    if isinstance(names, str):
        names = [names]

    elif not isinstance(names, (Sequence, Generator, Iterator)):
        raise ValueError(
            '"names" must be a string, or a Sequence of strings, but got "{}"'.format(
                type(names).__name__
            )
        )

    for name in names:
        _internal_commands[name] = (target, description)


def _get_registered_target(
    name: str, default: T | None = None
) -> InternalCommandCallback | T | None:
    target_info = _internal_commands.get(name, None)
    if target_info:
        return target_info[0]
    return default


def _exit_internal() -> NoReturn:
    raise ExitReplException()


def _help_internal() -> None:
    formatter = click.HelpFormatter()
    formatter.write_heading("REPL help")
    formatter.indent()

    with formatter.section("External Commands"):
        formatter.write_text('prefix external commands with "!"')

    with formatter.section("Internal Commands"):
        formatter.write_text('prefix internal commands with ":"')
        info_table = defaultdict(list)

        for mnemonic, target_info in _internal_commands.items():
            info_table[target_info[1]].append(mnemonic)

        formatter.write_dl(  # type: ignore[arg-type]
            (  # type: ignore[arg-type]
                ", ".join(map(":{}".format, sorted(mnemonics))),
                description,
            )
            for description, mnemonics in info_table.items()
        )

    print(formatter.getvalue())


_register_internal_command(["q", "quit", "exit"], _exit_internal, "exits the repl")
_register_internal_command(
    ["?", "h", "help"], _help_internal, "displays general help information"
)


def _execute_internal_and_sys_cmds(
    command: str,
    allow_internal_commands: bool = True,
    allow_system_commands: bool = True,
) -> list[str] | None:
    """
    Executes internal, system, and all the other registered click commands from the input
    """
    if allow_system_commands and dispatch_repl_commands(command):
        return None

    if allow_internal_commands and command.startswith(":"):
        handle_internal_commands(command)
        return None

    try:
        return split_arg_string(command)
    except ValueError as e:
        raise CommandLineParserError("{}".format(e))


def exit() -> NoReturn:
    """Exit the repl"""
    _exit_internal()


def dispatch_repl_commands(command: str) -> bool:
    """
    Execute system commands entered in the repl.

    System commands are all commands starting with "!".
    """
    if command.startswith("!"):
        os.system(command[1:])
        return True

    return False


def handle_internal_commands(command: str) -> None:
    """
    Run repl-internal commands.

    Repl-internal commands are all commands starting with ":".
    """
    target = _get_registered_target(command[1:], default=None)
    if target:
        target()
