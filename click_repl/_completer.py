from __future__ import annotations

import os
import typing as t
from glob import iglob
from typing import Generator

import click
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document

from .utils import _resolve_context, split_arg_string

__all__ = ["ClickCompleter"]

IS_WINDOWS = os.name == "nt"


# Handle backwards compatibility between Click<=7.0 and >=8.0
try:
    import click.shell_completion

    HAS_CLICK_V8 = True
    AUTO_COMPLETION_PARAM = "shell_complete"
except (ImportError, ModuleNotFoundError):
    import click._bashcomplete  # type: ignore[import]

    HAS_CLICK_V8 = False
    AUTO_COMPLETION_PARAM = "autocompletion"


class ClickCompleter(Completer):
    __slots__ = ("cli", "ctx", "parsed_args", "parsed_ctx", "ctx_command")

    def __init__(
        self,
        cli: click.MultiCommand,
        ctx: click.Context,
        show_only_unused: bool = False,
        shortest_only: bool = False,
    ) -> None:
        self.cli = cli
        self.ctx = ctx
        self.parsed_args: list[str] = []
        self.parsed_ctx = ctx
        self.ctx_command = ctx.command
        self.show_only_unused = show_only_unused
        self.shortest_only = shortest_only

    def _get_completion_from_autocompletion_functions(
        self,
        param: click.Parameter,
        autocomplete_ctx: click.Context,
        args: list[str],
        incomplete: str,
    ) -> list[Completion]:
        param_choices: list[Completion] = []

        if HAS_CLICK_V8:
            autocompletions = param.shell_complete(autocomplete_ctx, incomplete)
        else:
            autocompletions = param.autocompletion(  # type: ignore[attr-defined]
                autocomplete_ctx, args, incomplete
            )

        for autocomplete in autocompletions:
            if isinstance(autocomplete, tuple):
                param_choices.append(
                    Completion(
                        str(autocomplete[0]),
                        -len(incomplete),
                        display_meta=autocomplete[1],
                    )
                )

            elif HAS_CLICK_V8 and isinstance(
                autocomplete, click.shell_completion.CompletionItem
            ):
                param_choices.append(Completion(autocomplete.value, -len(incomplete)))

            else:
                param_choices.append(Completion(str(autocomplete), -len(incomplete)))

        return param_choices

    def _get_completion_from_choices_click_le_7(
        self, param: click.Parameter, incomplete: str
    ) -> list[Completion]:
        param_type = t.cast(click.Choice, param.type)

        if not getattr(param.type, "case_sensitive", True):
            incomplete = incomplete.lower()
            return [
                Completion(
                    choice,
                    -len(incomplete),
                    display=repr(choice) if " " in choice else choice,
                )
                for choice in param_type.choices  # type: ignore[attr-defined]
                if choice.lower().startswith(incomplete)
            ]

        else:
            return [
                Completion(
                    choice,
                    -len(incomplete),
                    display=repr(choice) if " " in choice else choice,
                )
                for choice in param_type.choices  # type: ignore[attr-defined]
                if choice.startswith(incomplete)
            ]

    def _get_completion_for_Path_types(
        self, param: click.Parameter, args: list[str], incomplete: str
    ) -> list[Completion]:
        if "*" in incomplete:
            return []

        choices: list[Completion] = []
        _incomplete = os.path.expandvars(incomplete)
        search_pattern = _incomplete.strip("'\"\t\n\r\v ").replace("\\\\", "\\") + "*"
        quote = ""

        if " " in _incomplete:
            for i in incomplete:
                if i in ("'", '"'):
                    quote = i
                    break

        for path in iglob(search_pattern):
            if " " in path:
                if quote:
                    path = quote + path
                else:
                    if IS_WINDOWS:
                        path = repr(path).replace("\\\\", "\\")
            else:
                if IS_WINDOWS:
                    path = path.replace("\\", "\\\\")

            choices.append(
                Completion(
                    path,
                    -len(incomplete),
                    display=os.path.basename(path.strip("'\"")),
                )
            )

        return choices

    def _get_completion_for_Boolean_type(
        self, param: click.Parameter, incomplete: str
    ) -> list[Completion]:
        boolean_mapping: dict[str, tuple[str, ...]] = {
            "true": ("1", "true", "t", "yes", "y", "on"),
            "false": ("0", "false", "f", "no", "n", "off"),
        }

        return [
            Completion(k, -len(incomplete), display_meta="/".join(v))
            for k, v in boolean_mapping.items()
            if any(i.startswith(incomplete) for i in v)
        ]

    def _get_completion_from_params(
        self,
        autocomplete_ctx: click.Context,
        args: list[str],
        param: click.Parameter,
        incomplete: str,
    ) -> list[Completion]:
        choices: list[Completion] = []
        param_type = param.type

        # shell_complete method for click.Choice is intorduced in click-v8
        if not HAS_CLICK_V8 and isinstance(param_type, click.Choice):
            choices.extend(
                self._get_completion_from_choices_click_le_7(param, incomplete)
            )

        elif isinstance(param_type, click.types.BoolParamType):
            choices.extend(self._get_completion_for_Boolean_type(param, incomplete))

        elif isinstance(param_type, (click.Path, click.File)):
            choices.extend(self._get_completion_for_Path_types(param, args, incomplete))

        elif getattr(param, AUTO_COMPLETION_PARAM, None) is not None:
            choices.extend(
                self._get_completion_from_autocompletion_functions(
                    param,
                    autocomplete_ctx,
                    args,
                    incomplete,
                )
            )

        return choices

    def _get_completion_for_cmd_args(
        self,
        ctx_command: click.Command,
        incomplete: str,
        autocomplete_ctx: click.Context,
        args: list[str],
    ) -> list[Completion]:
        choices: list[Completion] = []
        param_called = False

        for param in ctx_command.params:
            if isinstance(param.type, click.types.UnprocessedParamType):
                return []

            elif getattr(param, "hidden", False):
                continue

            elif isinstance(param, click.Option):
                opts = param.opts + param.secondary_opts
                previous_args = args[: param.nargs * -1]
                current_args = args[param.nargs * -1 :]

                # Show only unused opts
                already_present = any([opt in previous_args for opt in opts])
                hide = self.show_only_unused and already_present and not param.multiple

                # Show only shortest opt
                if (
                    self.shortest_only
                    and not incomplete  # just typed a space
                    # not selecting a value for a longer version of this option
                    and args[-1] not in opts
                ):
                    opts = [min(opts, key=len)]

                for option in opts:
                    # We want to make sure if this parameter was called
                    # If we are inside a parameter that was called, we want to show only
                    # relevant choices
                    if option in current_args:  # noqa: E203
                        param_called = True
                        break

                    elif option.startswith(incomplete) and not hide:
                        choices.append(
                            Completion(
                                option,
                                -len(incomplete),
                                display_meta=param.help or "",
                            )
                        )

                if param_called:
                    choices = self._get_completion_from_params(
                        autocomplete_ctx, args, param, incomplete
                    )
                    break

            elif isinstance(param, click.Argument):
                choices.extend(
                    self._get_completion_from_params(
                        autocomplete_ctx, args, param, incomplete
                    )
                )

        return choices

    def get_completions(
        self, document: Document, complete_event: CompleteEvent | None = None
    ) -> Generator[Completion, None, None]:
        # Code analogous to click._bashcomplete.do_complete

        args = split_arg_string(document.text_before_cursor, posix=False)

        choices: list[Completion] = []
        cursor_within_command = (
            document.text_before_cursor.rstrip() == document.text_before_cursor
        )

        if document.text_before_cursor.startswith(("!", ":")):
            return

        if args and cursor_within_command:
            # We've entered some text and no space, give completions for the
            # current word.
            incomplete = args.pop()
        else:
            # We've not entered anything, either at all or for the current
            # command, so give all relevant completions for this context.
            incomplete = ""

        if self.parsed_args != args:
            self.parsed_args = args
            try:
                self.parsed_ctx = _resolve_context(args, self.ctx)
            except Exception:
                return  # autocompletion for nonexistent cmd can throw here
            self.ctx_command = self.parsed_ctx.command

        if getattr(self.ctx_command, "hidden", False):
            return

        try:
            choices.extend(
                self._get_completion_for_cmd_args(
                    self.ctx_command, incomplete, self.parsed_ctx, args
                )
            )

            if isinstance(self.ctx_command, click.MultiCommand):
                incomplete_lower = incomplete.lower()

                for name in self.ctx_command.list_commands(self.parsed_ctx):
                    command = self.ctx_command.get_command(self.parsed_ctx, name)
                    if getattr(command, "hidden", False):
                        continue

                    elif name.lower().startswith(incomplete_lower):
                        choices.append(
                            Completion(
                                name,
                                -len(incomplete),
                                display_meta=getattr(command, "short_help", ""),
                            )
                        )

        except Exception as e:
            click.echo("{}: {}".format(type(e).__name__, str(e)))

        for item in choices:
            yield item
