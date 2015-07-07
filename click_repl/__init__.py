from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import get_input
from prompt_toolkit.history import History
import click
import click._bashcomplete
import click.parser
import shlex
import sys

class ClickCompleter(Completer):
    def __init__(self, cli):
        self.cli = cli

    def get_completions(self, document, complete_event):
        # Code analogous to click._bashcomplete.do_complete
        args = shlex.split(document.text_before_cursor)
        incomplete = args.pop()

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


def register_repl(group, name='repl'):
    @group.command(name=name)
    @click.pass_context
    def cli(old_ctx):
        '''
        Start an interactive shell. All subcommands are available in it.

        You can also pipe to this command to execute subcommands.
        '''

        # parent should be available, but we're not going to bother if not
        group_ctx = old_ctx.parent or old_ctx
        isatty = sys.stdin.isatty()
        if isatty:
            history = History()
            completer = ClickCompleter(group)
            def get_command():
                return get_input('> ', completer=completer, history=history)
        else:
            get_command = sys.stdin.readline

        while True:
            command = get_command()
            if not command:
                if isatty:
                    continue
                else:
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
