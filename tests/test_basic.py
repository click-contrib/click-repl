import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document
import pytest


@click.group()
def root_command():
    pass


c = ClickCompleter(root_command)


def test_arg_completion():
    @root_command.command()
    @click.argument("handler", type=click.Choice(("foo", "bar")))
    def arg_cmd(handler):
        pass

    completions = list(c.get_completions(Document("arg-cmd ")))
    assert set(x.text for x in completions) == {"foo", "bar"}


def test_option_completion():
    @root_command.command()
    @click.option("--handler", "-h", type=click.Choice(("foo", "bar")))
    def option_cmd(handler):
        pass

    completions = list(c.get_completions(Document("option-cmd ")))
    assert set(x.text for x in completions) == {"--handler", "-h"}

    completions = list(c.get_completions(Document("option-cmd --h")))
    assert set(x.text for x in completions) == {"--handler"}


def test_hidden_cmd():
    @root_command.command(hidden=True)
    @click.option("--handler", "-h")
    def hidden_cmd(handler):
        pass

    completions = list(c.get_completions(Document("hidden ")))
    assert set(x.text for x in completions) == {"arg-cmd", "option-cmd"}


def test_hidden_option():
    @root_command.command()
    @click.option("--handler", "-h", hidden=True)
    def hidden_option_cmd(handler):
        pass

    completions = list(c.get_completions(Document("hidden-option-cmd ")))
    assert set(x.text for x in completions) == set()


@pytest.mark.xfail
def test_wrong_shell_type_args():
    with pytest.raises(ValueError):
        completions = list(c.get_completions(Document("arg_cmd it's ")))
        assert set(x.text for x in completions) == set()


def test_completion_multilevel_command():
    @click.group()
    def root_group():
        pass

    @root_group.group()
    def first_level_command():
        pass

    @first_level_command.command()
    def second_level_command_one():
        pass

    @first_level_command.command()
    def second_level_command_two():
        pass

    c = ClickCompleter(root_group)

    completions = list(c.get_completions(Document("first-level-command ")))
    assert set(x.text for x in completions) == {
        "second-level-command-one", "second-level-command-two"
    }

    completions = list(c.get_completions(Document(" ")))
    assert set(x.text for x in completions) == {"first-level-command"}
