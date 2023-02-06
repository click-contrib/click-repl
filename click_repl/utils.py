import os
import shlex
import sys
from collections import defaultdict

import click.parser
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory

from .exceptions import ExitReplException, InternalCommandException  # noqa

# Handle backwards compatibility between Click 7.0 and 8.0
try:
    import click.shell_completion

    HAS_C8 = True
    AUTO_COMPLETION_PARAM = "shell_complete"

except (ImportError, ModuleNotFoundError):
    import click._bashcomplete

    HAS_C8 = False
    AUTO_COMPLETION_PARAM = "autocompletion"

# Handle click.exceptions.Exit introduced in Click 7.0
try:
    from click.exceptions import Exit as ClickExit
except ImportError:

    class ClickExit(RuntimeError):
        pass


_internal_commands = {}


PY2 = sys.version_info[0] == 2
if PY2:
    text_type = unicode  # noqa
else:
    text_type = str  # noqa


def _register_internal_command(names, target, description=None):
    if not hasattr(target, "__call__"):
        raise ValueError("Internal command must be a callable")

    if isinstance(names, str):
        names = [names]

    elif not isinstance(names, (list, tuple)):
        raise ValueError('"names" must be a string, list or a tuple')

    for name in names:
        _internal_commands[name] = (target, description)


def _get_registered_target(name, default=None):
    target_info = _internal_commands.get(name)
    if target_info:
        return target_info[0]
    return default


def _exit_internal():
    raise ExitReplException()


def _help_internal():
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

        formatter.write_dl(
            (
                ", ".join(map(":{0}".format, sorted(mnemonics))),
                description,
            )
            for description, mnemonics in info_table.items()
        )

    return formatter.getvalue()


_register_internal_command(["q", "quit", "exit"], _exit_internal, "exits the repl")
_register_internal_command(
    ["?", "h", "help"], _help_internal, "displays general help information"
)


class ClickCompleter(Completer):
    def __init__(self, cli, ctx=None):
        self.cli = cli
        self.ctx = ctx

    def _get_completion_from_autocompletion_functions(
        self, param, autocomplete_ctx, args, incomplete
    ):
        param_choices = []

        if HAS_C8:
            autocompletions = param.shell_complete(autocomplete_ctx, incomplete)
        else:
            autocompletions = param.autocompletion(autocomplete_ctx, args, incomplete)

        for autocomplete in autocompletions:
            if isinstance(autocomplete, tuple):
                param_choices.append(
                    Completion(
                        text_type(autocomplete[0]),
                        -len(incomplete),
                        display_meta=autocomplete[1],
                    )
                )

            elif HAS_C8 and isinstance(
                autocomplete, click.shell_completion.CompletionItem
            ):
                param_choices.append(
                    Completion(text_type(autocomplete.value), -len(incomplete))
                )

            else:
                param_choices.append(
                    Completion(text_type(autocomplete), -len(incomplete))
                )

        return param_choices

    def _get_completion_from_choices(self, param, incomplete):
        return [
            Completion(text_type(choice), -len(incomplete))
            for choice in param.type.choices
        ]

    def _get_completion_from_params(
        self,
        ctx_command,
        incomplete,
        autocomplete_ctx,
        args,
    ):
        choices, param_choices, param_called = [], [], False

        for param in ctx_command.params:
            if getattr(param, "hidden", False):
                continue

            if isinstance(param, click.Option):
                for options in (param.opts, param.secondary_opts):
                    for option in options:
                        choices.append(
                            Completion(
                                text_type(option),
                                -len(incomplete),
                                display_meta=param.help,
                            )
                        )

                        # We want to make sure if this parameter was called
                        if option in args[param.nargs * -1 :]:
                            param_called = True

                if (
                    param_called
                    and getattr(param, AUTO_COMPLETION_PARAM, None) is not None
                ):
                    param_choices.extend(
                        self._get_completion_from_autocompletion_functions(
                            param, autocomplete_ctx, args, incomplete
                        )
                    )

                elif not HAS_C8 and isinstance(param.type, click.Choice):
                    param_choices.extend(
                        self._get_completion_from_choices(param, incomplete)
                    )

            elif isinstance(param, click.Argument):
                if isinstance(param.type, click.Choice):
                    choices.extend(self._get_completion_from_choices(param, incomplete))

                elif (
                    not HAS_C8
                    and getattr(param, AUTO_COMPLETION_PARAM, None) is not None
                ):
                    choices = self._get_completion_from_autocompletion_functions(
                        param, autocomplete_ctx, args, incomplete
                    )

        return choices, param_choices, param_called

    def get_completions(self, document, complete_event=None):
        # Code analogous to click._bashcomplete.do_complete

        try:
            args = shlex.split(document.text_before_cursor)
        except ValueError:
            # Invalid command, perhaps caused by missing closing quotation.
            return

        cursor_within_command = (
            document.text_before_cursor.rstrip() == document.text_before_cursor
        )

        if args and cursor_within_command:
            # We've entered some text and no space, give completions for the
            # current word.
            incomplete = args.pop()
        else:
            # We've not entered anything, either at all or for the current
            # command, so give all relevant completions for this context.
            incomplete = ""

        # Resolve context based on click version
        if HAS_C8:
            ctx = click.shell_completion._resolve_context(self.cli, {}, "", args)
        else:
            ctx = click._bashcomplete.resolve_ctx(self.cli, "", args)

        if ctx is None:
            return

        autocomplete_ctx = self.ctx or ctx
        ctx_command = ctx.command

        if getattr(ctx_command, "hidden", False):
            return

        choices, param_choices, param_called = self._get_completion_from_params(
            ctx_command, incomplete, autocomplete_ctx, args
        )

        if isinstance(ctx_command, click.MultiCommand):
            for name in ctx_command.list_commands(ctx):
                command = ctx_command.get_command(ctx, name)
                if getattr(command, "hidden", False):
                    continue

                choices.append(
                    Completion(
                        text_type(name),
                        -len(incomplete),
                        display_meta=getattr(command, "short_help"),
                    )
                )

        # If we are inside a parameter that was called, we want to show only
        # relevant choices
        if param_called:
            choices = param_choices

        for item in choices:
            if item.text.startswith(incomplete):
                yield item


def bootstrap_prompt(prompt_kwargs, group, ctx=None):
    """
    Bootstrap prompt_toolkit kwargs or use user defined values.

    :param prompt_kwargs: The user specified prompt kwargs.
    """
    prompt_kwargs = prompt_kwargs or {}

    defaults = {
        "history": InMemoryHistory(),
        "completer": ClickCompleter(group, ctx=ctx),
        "message": "> ",
    }

    for key in defaults:
        default_value = defaults[key]
        if key not in prompt_kwargs:
            prompt_kwargs[key] = default_value

    return prompt_kwargs


def _exec_internal_and_sys_commands(
    command, allow_internal_commands=True, allow_system_commands=True
):
    if allow_system_commands and dispatch_repl_commands(command):
        return

    if allow_internal_commands:
        result = handle_internal_commands(command)
        if isinstance(result, str):
            click.echo(result)
            return


def repl(
    old_ctx, prompt_kwargs={}, allow_system_commands=True, allow_internal_commands=True
):
    """
    Start an interactive shell. All subcommands are available in it.

    :param old_ctx: The current Click context.
    :param prompt_kwargs: Parameters passed to
        :py:func:`prompt_toolkit.PromptSession`.

    If stdin is not a TTY, no prompt will be printed, but only commands read
    from stdin.

    """
    # parent should be available, but we're not going to bother if not
    group_ctx = old_ctx.parent or old_ctx
    group = group_ctx.command
    isatty = sys.stdin.isatty()

    # Delete the REPL command from those available, as we don't want to allow
    # nesting REPLs (note: pass `None` to `pop` as we don't want to error if
    # REPL command already not present for some reason).
    repl_command_name = old_ctx.command.name
    if isinstance(group_ctx.command, click.CommandCollection):
        available_commands = {
            cmd_name: cmd_obj
            for source in group_ctx.command.sources
            for cmd_name, cmd_obj in source.commands.items()
        }
    else:
        available_commands = group_ctx.command.commands

    original_command = available_commands.pop(repl_command_name, None)
    prompt_kwargs = bootstrap_prompt(prompt_kwargs, group, ctx=group_ctx)
    session = PromptSession(**prompt_kwargs)

    if isatty:

        def get_command():
            return session.prompt()

    else:
        get_command = sys.stdin.readline

    while True:
        try:
            command = get_command()
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

        if not command:
            if isatty:
                continue
            else:
                break

        _exec_internal_and_sys_commands(
            command,
            allow_internal_commands=allow_internal_commands,
            allow_system_commands=allow_system_commands,
        )

        try:
            args = shlex.split(command)
        except ValueError as e:
            click.echo("{}: {}".format(type(e).__name__, e))
            return

        try:
            # default_map passes the top-level params to the new group to
            # support top-level required params that would reject the
            # invocation if missing.
            with group.make_context(
                None, args, parent=group_ctx, default_map=old_ctx.params
            ) as ctx:
                group.invoke(ctx)
                ctx.exit()

        except click.ClickException as e:
            e.show()
        except (ClickExit, SystemExit):
            pass

        except ExitReplException:
            break

    if original_command is not None:
        available_commands[repl_command_name] = original_command


def register_repl(group, name="repl"):
    """Register :func:`repl()` as sub-command *name* of *group*."""
    group.command(name=name)(click.pass_context(repl))


def exit():
    """Exit the repl"""
    _exit_internal()


def dispatch_repl_commands(command):
    """Execute system commands entered in the repl.

    System commands are all commands starting with "!".

    """
    if command.startswith("!"):
        os.system(command[1:])
        return True

    return False


def handle_internal_commands(command):
    """Run repl-internal commands.

    Repl-internal commands are all commands starting with ":".

    """
    if command.startswith(":"):
        target = _get_registered_target(command[1:], default=None)
        if target:
            return target()
