import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document
import pytest


@click.group()
def root_command():
    pass


c = ClickCompleter(root_command, click.Context(root_command))


def test_arg_completion():
    @root_command.command()
    @click.argument("handler", type=click.Choice(("foo", "bar")))
    def arg_cmd(handler):
        pass

    completions = list(c.get_completions(Document("arg-cmd ")))
    assert {x.text for x in completions} == {"foo", "bar"}


@root_command.command()
@click.option("--handler", "-h", type=click.Choice(("foo", "bar")), help="Demo option")
def option_cmd(handler):
    pass


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("option-cmd ", {"--handler", "-h"}),
        ("option-cmd -h", {"-h"}),
        ("option-cmd --h", {"--handler"}),
    ],
)
def test_option_completion(test_input, expected):
    completions = list(c.get_completions(Document(test_input)))
    assert {x.text for x in completions} == expected
