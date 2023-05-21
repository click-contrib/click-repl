import click
import pytest

import click_repl
from tests import mock_stdin


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

    assert capsys.readouterr().out.replace("\r\n", "\n") == "Foo!\n"


def test_group_command_called(capsys):
    @click.group(invoke_without_command=True)
    @click.pass_context
    def cli(ctx):
        print("cli()")
        if ctx.invoked_subcommand is None:
            click_repl.repl(ctx)

    @cli.command()
    def foo():
        print("Foo!")

    @cli.command()
    def bar():
        print("Bar!")

    with mock_stdin("foo\nbar\n"):
        with pytest.raises(SystemExit):
            cli(args=[], prog_name="test_group_called")

    assert capsys.readouterr().out.replace("\r\n", "\n") == (
        "cli()\ncli()\nFoo!\ncli()\nBar!\n"
    )


@click.group(invoke_without_command=True)
@click.argument("argument", required=False)
@click.pass_context
def cli_arg_required_false(ctx, argument):
    if ctx.invoked_subcommand is None:
        click_repl.repl(ctx)


@cli_arg_required_false.command()
def foo():
    print("Foo")


@pytest.mark.parametrize(
    "args, stdin, expected_err, expected_output",
    [
        ([], "foo\n", click_repl.exceptions.InvalidGroupFormat, ""),
        (["temp_arg"], "", SystemExit, ""),
        (["temp_arg"], "foo\n", SystemExit, "Foo\n"),
    ],
)
def test_group_argument_with_required_false(
    capsys, args, stdin, expected_err, expected_output
):
    with pytest.raises(expected_err):
        with mock_stdin(stdin):
            cli_arg_required_false(args=args, prog_name="cli_arg_required_false")

    assert capsys.readouterr().out.replace("\r\n", "\n") == expected_output


@click.group(invoke_without_command=True)
@click.argument("argument")
@click.option("--option1", default=1, type=click.STRING)
@click.option("--option2")
@click.pass_context
def cmd(ctx, argument, option1, option2):
    print(f"cli({argument}, {option1}, {option2})")
    if ctx.invoked_subcommand is None:
        click_repl.repl(ctx)


@cmd.command("foo")
def foo2():
    print("Foo!")


@pytest.mark.parametrize(
    "args, expected",
    [
        (["hi"], "cli(hi, 1, None)\ncli(hi, 1, None)\nFoo!\n"),
        (
            ["--option1", "opt1", "hi"],
            "cli(hi, opt1, None)\ncli(hi, opt1, None)\nFoo!\n",
        ),
        (["--option2", "opt2", "hi"], "cli(hi, 1, opt2)\ncli(hi, 1, opt2)\nFoo!\n"),
        (
            ["--option1", "opt1", "--option2", "opt2", "hi"],
            "cli(hi, opt1, opt2)\ncli(hi, opt1, opt2)\nFoo!\n",
        ),
    ],
)
def test_group_with_multiple_optional_args(capsys, args, expected):
    with pytest.raises(SystemExit):
        with mock_stdin("foo\n"):
            cmd(args=args, prog_name="test_group_with_multiple_args")
    assert capsys.readouterr().out.replace("\r\n", "\n") == expected


def test_inputs(capsys):
    @click.group(invoke_without_command=True)
    @click.pass_context
    def cli(ctx):
        if ctx.invoked_subcommand is None:
            ctx.invoke(repl)

    @cli.command()
    @click.pass_context
    def repl(ctx):
        click_repl.repl(ctx)

    try:
        cli(args=["repl"], prog_name="test_inputs")

    except (SystemExit, Exception) as e:
        if (
            type(e).__name__ == "prompt_toolkit.output.win32.NoConsoleScreenBufferError"
            and str(e) == "No Windows console found. Are you running cmd.exe?"
        ):
            pass

    captured_stdout = capsys.readouterr().out.replace("\r\n", "\n")
    assert captured_stdout == ""
