import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document
import pytest


@click.group()
def root_command():
    pass


c = ClickCompleter(root_command, click.Context(root_command))


@pytest.mark.skipif(
    click.__version__[0] > "7",
    reason="click-v7 old autocomplete function is not available, so skipped",
)
def test_click7_autocomplete_option():
    def shell_complete_func(ctx, args, incomplete):
        return [name for name in ("foo", "bar") if name.startswith(incomplete)]

    @root_command.command()
    @click.option("--handler", autocompletion=shell_complete_func)
    def autocompletion_opt_cmd2(handler):
        pass

    completions = list(
        c.get_completions(Document("autocompletion-opt-cmd2 --handler "))
    )
    assert {x.text for x in completions} == {"foo", "bar"}
