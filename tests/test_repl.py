import click
import click_repl
import platform
import pytest


def test_simple_repl(capfd):
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

    captured_stdout = capfd.readouterr().out
<<<<<<< HEAD
=======
    assert (
        captured_stdout.replace("\r\n", "\n")
        == """Usage: pytest [OPTIONS] COMMAND [ARGS]...
>>>>>>> c28ab260455a8aa6a6b6b1d7a8bae4ef77f6f493

    if platform.system() == "Linux":
        expected_output = ""
    else:
        expected_output = """Usage: pytest [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      bar
      foo
      repl  Start an interactive shell.
    """

    assert captured_stdout.replace("\r\n", "\n") == expected_output


def test_exit_repl_function():
    with pytest.raises(click_repl.exceptions.ExitReplException):
        click_repl.utils.exit()


def test_inputs():
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
<<<<<<< HEAD
    except Exception as e:
=======
    except (SystemExit, Exception) as e:
>>>>>>> c28ab260455a8aa6a6b6b1d7a8bae4ef77f6f493
        if (
            type(e).__name__ == "prompt_toolkit.output.win32.NoConsoleScreenBufferError"
            and str(e) == "No Windows console found. Are you running cmd.exe?"
        ):
            pass
<<<<<<< HEAD
=======

>>>>>>> c28ab260455a8aa6a6b6b1d7a8bae4ef77f6f493
