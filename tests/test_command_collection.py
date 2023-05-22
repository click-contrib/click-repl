import click
from click_repl import ClickCompleter, repl
from prompt_toolkit.document import Document
import pytest


def test_command_collection():
    @click.group()
    def foo_group():
        pass

    @foo_group.command()
    def foo_cmd():
        pass

    @click.group()
    def foobar_group():
        pass

    @foobar_group.command()
    def foobar_cmd():
        pass

    cmd = click.CommandCollection(sources=(foo_group, foobar_group))
    c = ClickCompleter(cmd, click.Context(cmd))
    completions = list(c.get_completions(Document("foo")))

    assert {x.text for x in completions} == {"foo-cmd", "foobar-cmd"}


@click.group(invoke_without_command=True)
@click.option("--user", required=True)
@click.pass_context
def cli(ctx, user):
    if ctx.invoked_subcommand is None:
        click.echo("Top-level user: {}".format(user))
        repl(ctx)


@cli.command()
@click.option("--user")
def c1(user):
    click.echo("Executed C1 with {}!".format(user))


c = ClickCompleter(cli, click.Context(cli))


@pytest.mark.parametrize(
    "test_input,expected", [(" ", {"--user", "c1"}), ("c1 ", {"--user"})]
)
def test_subcommand_invocation_from_group(test_input, expected):
    completions = list(c.get_completions(Document(test_input)))
    assert {x.text for x in completions} == expected
