import click
from click_repl import ClickCompleter, repl
from prompt_toolkit.document import Document


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

    c = ClickCompleter(click.CommandCollection(sources=(foo_group, foobar_group)))
    completions = list(c.get_completions(Document("foo")))

    assert set(x.text for x in completions) == {"foo-cmd", "foobar-cmd"}


def test_subcommand_invocation():
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

    c = ClickCompleter(cli)

    completions = list(c.get_completions(Document(" ")))
    assert set(x.text for x in completions) == {"--user", "c1"}

    completions = list(c.get_completions(Document("c1 ")))
    assert set(x.text for x in completions) == {"--user"}
