import click
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
