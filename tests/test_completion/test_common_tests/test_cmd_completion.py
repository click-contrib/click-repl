import click
import pytest
from unittest import TestCase
from prompt_toolkit.document import Document
from click_repl import ClickCompleter


@click.group()
def cli():
    pass


@cli.group()
def cmd():
    pass


@cmd.command()
def subcmd():
    pass


class Test_Command_Autocompletion(TestCase):
    def setUp(self):
        self.c = ClickCompleter(cli, click.Context(cli))

    def test_valid_subcmd(self):
        res = list(self.c.get_completions(Document("cmd s")))
        self.assertListEqual([i.text for i in res], ["subcmd"])

    def test_not_valid_subcmd(self):
        try:
            res = list(self.c.get_completions(Document("not cmd")))
        except Exception as e:
            self.fail(f"Autocompletion raised exception: {e}")
        self.assertListEqual(res, [])


@pytest.mark.parametrize("prefix", ["", "group "])
@pytest.mark.parametrize(
    "help_text,short_help,expected",
    [
        ("Set parameters. Additional details go here.", None, "Set parameters."),
        ("Set parameters.", "Custom summary", "Custom summary"),
        (None, None, ""),
    ],
)
def test_command_completion_displays_short_help(prefix, help_text, short_help, expected):
    """Show Click's short help for both root and nested command completions."""

    @click.group()
    def app():
        pass

    @app.group()
    def group():
        pass

    def action():
        pass

    action.__doc__ = help_text
    command = click.command(name="sample", short_help=short_help)(action)
    app.add_command(command)
    group.add_command(command)
    completer = ClickCompleter(app, click.Context(app))

    completions = list(completer.get_completions(Document(prefix + "sam")))

    assert [completion.text for completion in completions] == ["sample"]
    assert completions[0].display_meta_text == expected
