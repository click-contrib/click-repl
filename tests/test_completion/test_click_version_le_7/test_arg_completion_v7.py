import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document
import pytest


@click.group()
def root_command():
    pass


c = ClickCompleter(root_command, click.Context(root_command))


@pytest.mark.skipif(
    int(click.__version__[0]) != 7,
    reason="click-v7 old autocomplete function is not available, so skipped",
)
def test_click7_autocomplete_arg():
    def shell_complete_func(ctx, args, incomplete):
        return [name for name in ("foo", "bar") if name.startswith(incomplete)]

    @root_command.command("autocompletionCmd")
    @click.argument("handler", autocompletion=shell_complete_func)
    def autocompletionCmd(handler):
        pass

    completions = list(c.get_completions(Document("autocompletionCmd ")))
    assert {x.text for x in completions} == {"foo", "bar"}


@pytest.mark.skipif(
    int(click.__version__[0]) != 7,
    reason="click-v7 old autocomplete function is not available, so skipped",
)
@pytest.mark.parametrize(
    "test_input, suggestions, display_txts",
    [
        (
            "tupleTypeAutocompletion ",
            {"Hi", "Please", "Hey", "Aye"},
            {"hi", "please", "hey", "aye"},
        ),
        ("tupleTypeAutocompletion h", {"Hi", "Hey"}, {"hi", "hey"}),
    ],
)
def test_tuple_return_type_shell_complete_func_click7(
    test_input, suggestions, display_txts
):
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

    @root_command.command("tupleTypeAutocompletion")
    @click.argument("foo", autocompletion=return_type_tuple_shell_complete)
    def tupleTypeAutocompletion(foo):
        pass

    completions = c.get_completions(Document(test_input))
    assert {x.text for x in completions} == suggestions

    if click.__version__[0] <= "6":
        assert {x.display_meta[0][-1] for x in completions} == display_txts
