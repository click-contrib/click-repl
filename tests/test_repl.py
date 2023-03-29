import contextlib
import sys

import click
import click_repl
import pytest

from io import StringIO


@contextlib.contextmanager
def mock_stdin(text):
    old_stdin = sys.stdin
    try:
        sys.stdin = StringIO(text)
        yield sys.stdin
    finally:
        sys.stdin = old_stdin


def test_simple_repl():
    @click.group()
    def cli():
        pass

    @cli.command()
    @click.option("--baz", is_flag=True)
    def foo(baz):
        print("Foo!")

    @cli.command()
    @click.option("--foo", is_flag=True)
    def bar(foo):
        print("Bar!")

    click_repl.register_repl(cli)

    with pytest.raises(SystemExit):
        cli(args=[], prog_name="test_simple_repl")


def test_repl_dispatches_subcommand(capsys):
    @click.group(invoke_without_command=True)
    @click.pass_context
    def cli(ctx):
        if ctx.invoked_subcommand is None:
            click_repl.repl(ctx)

    @cli.command()
    def foo():
        print("Foo!")

    with mock_stdin("foo\n"):
        with pytest.raises(SystemExit):
            cli(args=[], prog_name="test_repl_dispatch_subcommand")
    assert capsys.readouterr().out == "Foo!\n"


def test_group_command_called_on_each_subcommands(capsys):
    @click.group(invoke_without_command=True)
    @click.pass_context
    def cli(ctx):
        if ctx.invoked_subcommand is None:
            click_repl.repl(ctx)
        else:
            print("cli()")

    @cli.command()
    def foo():
        print("Foo!")

    @cli.command()
    def bar():
        print("Bar!")

    with mock_stdin("foo\nbar\n"):
        with pytest.raises(SystemExit):
            cli(args=[], prog_name="test_group_command_called_on_each_subcommands")
    assert capsys.readouterr().out == "cli()\nFoo!\ncli()\nBar!\n"


def test_group_argument_are_preserved(capsys):
    @click.group(invoke_without_command=True)
    @click.argument("argument")
    @click.pass_context
    def cli(ctx, argument):
        if ctx.invoked_subcommand is None:
            click_repl.repl(ctx)
        else:
            print("cli(%s)" % argument)

    @cli.command()
    @click.argument("argument")
    def foo(argument):
        print("Foo: %s!" % argument)

    with mock_stdin("foo bar\n"):
        with pytest.raises(SystemExit):
            cli(args=["arg"], prog_name="test_group_argument_are_preserved")
    assert capsys.readouterr().out == "cli(arg)\nFoo: bar!\n"


def test_chain_commands(capsys):
    @click.group(invoke_without_command=True, chain=True)
    @click.pass_context
    def cli(ctx):
        if ctx.invoked_subcommand is None:
            click_repl.repl(ctx)
        else:
            print("cli()")

    @cli.command()
    def foo():
        print("Foo!")

    @cli.command()
    def bar():
        print("Bar!")

    with mock_stdin("foo bar\n"):
        with pytest.raises(SystemExit):
            cli(args=[], prog_name="test_chain_commands")
    assert capsys.readouterr().out == "cli()\nFoo!\nBar!\n"


def test_exit_repl_function():
    with pytest.raises(click_repl.exceptions.ExitReplException):
        click_repl.utils.exit()


def test_inputs(capfd):
    @click.group(invoke_without_command=True)
    @click.pass_context
    def cli(ctx):
        if ctx.invoked_subcommand is None:
            ctx.invoke(repl)

    @cli.command()
    def repl():
        click_repl.repl(click.get_current_context())

    try:
        cli(args=[], prog_name="test_inputs")
    except (SystemExit, Exception) as e:
        if (
            type(e).__name__ == "prompt_toolkit.output.win32.NoConsoleScreenBufferError"
            and str(e) == "No Windows console found. Are you running cmd.exe?"
        ):
            pass

    captured_stdout = capfd.readouterr().out.replace("\r\n", "\n")
    assert captured_stdout == ""
