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
def test_click7_autocomplete_arg():
    def shell_complete_func(ctx, args, incomplete):
        return [name for name in ("foo", "bar") if name.startswith(incomplete)]

    @root_command.command()
    @click.argument("handler", autocompletion=shell_complete_func)
    def autocompletion_arg_cmd2(handler):
        pass

    completions = list(c.get_completions(Document("autocompletion-arg-cmd2 ")))
    assert {x.text for x in completions} == {"foo", "bar"}


@pytest.mark.skipif(
    click.__version__[0] > "7",
    reason="click-v7 old autocomplete function is not available, so skipped",
)
def test_tuple_return_type_shell_complete_func_click7():
    def return_type_tuple_shell_complete(ctx, args, incomplete):
        return [
            i
            for i in [
                ("Hi", "hi"),
                ("Please", "please"),
                ("Hey", "hey"),
                ("Aye", "aye"),
            ]
            if i[1].startswith(incomplete)
        ]

    @root_command.command()
    @click.argument("foo", autocompletion=return_type_tuple_shell_complete)
    def tuple_type_autocompletion_cmd(foo):
        pass

    completions = list(c.get_completions(Document("tuple-type-autocompletion-cmd ")))
    assert {x.text for x in completions} == {"Hi", "Please", "Hey", "Aye"} and {
        x.display_meta[0][-1] for x in completions
    } == {"hi", "please", "hey", "aye"}

    completions = list(c.get_completions(Document("tuple-type-autocompletion-cmd h")))
    assert {x.text for x in completions} == {"Hi", "Hey"} and {
        x.display_meta[0][-1] for x in completions
    } == {"hi", "hey"}
