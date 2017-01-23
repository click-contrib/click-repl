from collections import defaultdict
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.shortcuts import prompt
import click
import click._bashcomplete
import click.parser
import os
import shlex
import sys
import six
from .exceptions import InternalCommandException, ExitReplException  # noqa


__version__ = '0.1.1'

_internal_commands = dict()


def _register_internal_command(names, target, description=None):
    if not hasattr(target, '__call__'):
        raise ValueError('Internal command must be a callable')

    if isinstance(names, six.string_types):
        names = [names]
    elif not isinstance(names, (list, tuple)):
        raise ValueError('"names" must be a string or a list / tuple')

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
    formatter.write_heading('REPL help')
    formatter.indent()
    with formatter.section('External Commands'):
        formatter.write_text('prefix external commands with "!"')
    with formatter.section('Internal Commands'):
        formatter.write_text('prefix internal commands with ":"')
        info_table = defaultdict(list)
        for mnemonic, target_info in six.iteritems(_internal_commands):
            info_table[target_info[1]].append(mnemonic)
        formatter.write_dl(
            (', '.join((':{0}'.format(mnemonic)
                        for mnemonic in sorted(mnemonics))), description)
            for description, mnemonics in six.iteritems(info_table)
        )
    return formatter.getvalue()


_register_internal_command(['q', 'quit', 'exit'], _exit_internal,
                           'exits the repl')
_register_internal_command(['?', 'h', 'help'], _help_internal,
                           'displays general help information')


class ClickCompleter(Completer):
    def __init__(self, cli):
        self.cli = cli

    def get_completions(self, document, complete_event=None):
        # Code analogous to click._bashcomplete.do_complete

        try:
            args = shlex.split(document.text_before_cursor)
        except ValueError:
            # Invalid command, perhaps caused by missing closing quotation.
            return

        cursor_within_command = \
            document.text_before_cursor.rstrip() == document.text_before_cursor

        if args and cursor_within_command:
            # We've entered some text and no space, give completions for the
            # current word.
            incomplete = args.pop()
        else:
            # We've not entered anything, either at all or for the current
            # command, so give all relevant completions for this context.
            incomplete = ''

        ctx = click._bashcomplete.resolve_ctx(self.cli, '', args)
        if ctx is None:
            return

        choices = []
        for param in ctx.command.params:
            if not isinstance(param, click.Option):
                continue
            for options in (param.opts, param.secondary_opts):
                for o in options:
                    choices.append(Completion(o, -len(incomplete),
                                              display_meta=param.help))

        if isinstance(ctx.command, click.MultiCommand):
            for name in ctx.command.list_commands(ctx):
                command = ctx.command.get_command(ctx, name)
                choices.append(Completion(
                    name,
                    -len(incomplete),
                    display_meta=getattr(command, 'short_help')
                ))

        for item in choices:
            if item.text.startswith(incomplete):
                yield item


def repl(old_ctx, prompt_kwargs=None):
    """
    Start an interactive shell. All subcommands are available in it.

    :param old_ctx: The current Click context.
    :param prompt_kwargs: Parameters passed to
        :py:func:`prompt_toolkit.shortcuts.prompt`.

    If stdin is not a TTY, no prompt will be printed, but only commands read
    from stdin.

    """
    # parent should be available, but we're not going to bother if not
    group_ctx = old_ctx.parent or old_ctx
    group = group_ctx.command
    isatty = sys.stdin.isatty()

    if isatty:
        prompt_kwargs = prompt_kwargs or {}
        prompt_kwargs.setdefault('message', u'> ')
        history = prompt_kwargs.pop('history', None) \
            or InMemoryHistory()
        completer = prompt_kwargs.pop('completer', None) \
            or ClickCompleter(group)

        def get_command():
            return prompt(completer=completer, history=history,
                          **prompt_kwargs)
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

        if dispatch_repl_commands(command):
            continue

        try:
            result = handle_internal_commands(command)
            if isinstance(result, six.string_types):
                click.echo(result)
                continue
        except ExitReplException:
            break

        args = shlex.split(command)

        try:
            with group.make_context(None, args, parent=group_ctx) as ctx:
                group.invoke(ctx)
                ctx.exit()
        except click.ClickException as e:
            e.show()
        except SystemExit:
            pass


def register_repl(group, name='repl'):
    """Register :func:`repl()` as sub-command *name* of *group*."""
    group.command(name=name)(click.pass_context(repl))


def dispatch_repl_commands(command):
    """Execute system commands entered in the repl.

    System commands are all commands starting with "!".

    """
    if command.startswith('!'):
        os.system(command[1:])
        return True

    return False


def handle_internal_commands(command):
    """Run repl-internal commands.

    Repl-internal commands are all commands starting with ":".

    """
    if command.startswith(':'):
        target = _get_registered_target(command[1:], default=None)
        if target:
            return target()
