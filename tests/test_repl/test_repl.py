import click
import click_repl
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

    captured_stdout = capfd.readouterr().out.replace("\r\n", "\n")
    assert (
        captured_stdout
        == """Usage: pytest [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  bar
  foo
  repl  Start an interactive shell.
"""
    )


def test_repl_no_handle_internal_cmds(capfd):
    @click.group(invoke_without_command=True)
    @click.pass_context
    def cli(ctx):
        if ctx.invoked_subcommand is None:
            ctx.invoke(repl)

    @cli.command()
    def repl():
        click_repl.repl(click.get_current_context(), allow_internal_commands=False)

    @cli.command()
    @click.option("--baz", is_flag=True)
    def foo(baz):
        print("Foo!")

    @cli.command()
    @click.option("--foo", is_flag=True)
    def bar(foo):
        print("Bar!")

    # with pytest.raises(SystemExit):
    #     cli()


def test_repl_no_handle_system_cmds(capfd):
    @click.group(invoke_without_command=True)
    @click.pass_context
    def cli(ctx):
        if ctx.invoked_subcommand is None:
            ctx.invoke(repl)

    @cli.command()
    def repl():
        click_repl.repl(click.get_current_context(), allow_system_commands=False)

    @cli.command()
    @click.option("--baz", is_flag=True)
    def foo(baz):
        print("Foo!")

    @cli.command()
    @click.option("--foo", is_flag=True)
    def bar(foo):
        print("Bar!")

    # with pytest.raises(SystemExit):
    #     cli()


# '''REPL help:

#   External Commands:
#     prefix external commands with "!"

#   Internal Commands:
#     prefix internal commands with ":"
#     :exit, :q, :quit  exits the repl
#     :?, :h, :help     displays general help information

# '''
