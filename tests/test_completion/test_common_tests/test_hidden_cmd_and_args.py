import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document
import pytest


@click.group()
def root_command():
    pass


c = ClickCompleter(root_command, click.Context(root_command))


@pytest.mark.skipif(
    int(click.__version__[0]) < 7,
    reason="Hidden keyword is introduced in click v7, so skipped",
)
def test_hidden_cmd():
    @root_command.command("hiddenCmd", hidden=True)
    @click.option("--handler", "-h")
    def hiddenCmd(handler):
        pass

    completions = c.get_completions(Document("hiddenC"))
    assert {x.text for x in completions} == set()


@pytest.mark.skipif(
    int(click.__version__[0]) < 7,
    reason="Hidden keyword is introduced in click v7, so skipped",
)
def test_hidden_option():
    @root_command.command("hiddenOptionCmd")
    @click.option("--handler", "-h", hidden=True)
    def hiddenOptionCmd(handler):
        pass

    completions = c.get_completions(Document("hiddenOptionCmd "))
    assert {x.text for x in completions} == set()


@pytest.mark.skipif(
    int(click.__version__[0]) < 7,
    reason="Hidden keyword is introduced in click v7, so skipped",
)
@pytest.mark.parametrize(
    "test_input", ["argsChoicesHiddenCmd foo ", "argsChoicesHiddenCmd --handler "]
)
def test_args_of_hidden_command(test_input):
    @root_command.command("argsChoicesHiddenCmd", hidden=True)
    @click.argument("handler1", type=click.Choice(("foo", "bar")))
    @click.option("--handler2", type=click.Choice(("foo", "bar")))
    def argsChoicesHiddenCmd(handler):
        pass

    completions = c.get_completions(Document(test_input))
    assert {x.text for x in completions} == set()
