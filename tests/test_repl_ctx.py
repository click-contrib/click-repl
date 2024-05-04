from __future__ import annotations

import click
import pytest

import click_repl
from tests import mock_stdin


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click_repl.repl(ctx)


@cli.command()
def hello():
    print("Hello!")


@cli.command()
@click_repl.pass_context
def history_test(repl_ctx):
    print(list(repl_ctx.history()))


def test_repl_ctx_history(capsys):
    with mock_stdin("hello\nhistory-test\n"):
        with pytest.raises(SystemExit):
            cli(args=[], prog_name="test_repl_ctx_history")

    assert (
        capsys.readouterr().out.replace("\r\n", "\n")
        == "Hello!\n['history-test', 'hello']\n"
    )


@cli.command()
@click_repl.pass_context
def prompt_test(repl_ctx):
    print(repl_ctx.prompt)


def test_repl_ctx_prompt(capsys):
    with mock_stdin("prompt-test\n"):
        with pytest.raises(SystemExit):
            cli(args=[], prog_name="test_repl_ctx_history")

    assert capsys.readouterr().out.replace("\r\n", "\n") == "None\n"
