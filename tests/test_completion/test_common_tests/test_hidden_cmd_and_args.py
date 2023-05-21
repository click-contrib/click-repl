import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document
import pytest


@click.group()
def root_command():
    pass


c = ClickCompleter(root_command, click.Context(root_command))


def test_hidden_cmd():
    @root_command.command('hiddenCmd', hidden=True)
    @click.option("--handler", "-h")
    def hiddenCmd(handler):
        pass

    completions = c.get_completions(Document("hiddenC"))
    assert {x.text for x in completions} == set()


def test_hidden_option():
    @root_command.command('hiddenOptionCmd')
    @click.option("--handler", "-h", hidden=True)
    def hiddenOptionCmd(handler):
        pass

    completions = c.get_completions(Document("hiddenOptionCmd "))
    assert {x.text for x in completions} == set()


@pytest.mark.parametrize("test_input", [
    "argsChoicesHiddenCmd foo ",
    "argsChoicesHiddenCmd --handler "
])
def test_args_of_hidden_command(test_input):
    @root_command.command('argsChoicesHiddenCmd', hidden=True)
    @click.argument("handler1", type=click.Choice(("foo", "bar")))
    @click.option("--handler2", type=click.Choice(("foo", "bar")))
    def argsChoicesHiddenCmd(handler):
        pass

    completions = c.get_completions(Document(test_input))
    assert {x.text for x in completions} == set()


@click.group()
def root_group():
    pass

@root_group.group('firstLevelCommand')
def firstLevelCommand():
    pass

@firstLevelCommand.command('secondLevelCommandOne')
def secondLevelCommandOne():
    pass

@firstLevelCommand.command('secondLevelCommandTwo')
def secondLevelCommandTwo():
    pass


c2 = ClickCompleter(root_group, click.Context(root_group))


@pytest.mark.parametrize("test_input, expected", [
    ("firstLevelCommand ", {
        "secondLevelCommandOne",
        "secondLevelCommandTwo",
    }),
    (" ", {"firstLevelCommand"})
])
def test_completion_multilevel_command(test_input, expected):
    completions = c2.get_completions(Document(test_input))
    assert set(x.text for x in completions) == expected
