import click
import click_repl
import pytest


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
        cli()


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
        cli()
    except (SystemExit, Exception) as e:
        if (
            type(e).__name__ == "prompt_toolkit.output.win32.NoConsoleScreenBufferError"
            and str(e) == "No Windows console found. Are you running cmd.exe?"
        ):
            pass

    captured_stdout = capfd.readouterr().out.replace("\r\n", "\n")
    assert captured_stdout == ""
