import click
from click_repl import ClickCompleter, repl
from prompt_toolkit.document import Document
import pytest


def test_command_collection():
    @click.group()
    def foo_group():
        pass

    @foo_group.command()
    def foo():
        pass

    @click.group()
    def foobar_group():
        pass

    @foobar_group.command()
    def foobar():
        pass

    cmd_collection = click.CommandCollection(sources=(foo_group, foobar_group))
    c = ClickCompleter(cmd_collection, click.Context(cmd_collection))
    completions = list(c.get_completions(Document("foo")))

    assert {x.text for x in completions} == {"foo", "foobar"}


@click.group(invoke_without_command=True)
@click.option("--user", required=True)
@click.pass_context
def cli(ctx, user):
    if ctx.invoked_subcommand is None:
        click.echo(f"Top-level user: {user}")
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


@click.group()
def root_group():
    pass


@root_group.group("firstLevelCommand")
def firstLevelCommand():
    pass


@firstLevelCommand.command("secondLevelCommandOne")
def secondLevelCommandOne():
    pass


@firstLevelCommand.command("secondLevelCommandTwo")
def secondLevelCommandTwo():
    pass


c2 = ClickCompleter(root_group, click.Context(root_group))


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (
            "firstLevelCommand ",
            {
                "secondLevelCommandOne",
                "secondLevelCommandTwo",
            },
        ),
        (" ", {"firstLevelCommand"}),
    ],
)
def test_completion_multilevel_command(test_input, expected):
    completions = c2.get_completions(Document(test_input))
    assert set(x.text for x in completions) == expected
