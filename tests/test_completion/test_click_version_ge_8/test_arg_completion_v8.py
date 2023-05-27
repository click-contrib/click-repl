import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document
import pytest


@click.group()
def root_command():
    pass


c = ClickCompleter(root_command, click.Context(root_command))

with pytest.importorskip(
    "click.shell_complete.CompletionItem",
    minversion="8.0.0",
    reason="click-v8 built-in shell complete is not available, so skipped",
) as CompletionItem:

    def test_shell_complete_arg_v8_class_type():
        class MyVar(click.ParamType):
            name = "myvar"

            def shell_complete(self, ctx, param, incomplete):
                return [
                    CompletionItem(name)
                    for name in ("foo", "bar")
                    if name.startswith(incomplete)
                ]

        @root_command.command()
        @click.argument("handler", type=MyVar())
        def autocompletion_arg_cmd(handler):
            pass

        completions = list(c.get_completions(Document("autocompletion-cmd ")))
        assert {x.text for x in completions} == {"foo", "bar"}


with pytest.importorskip(
    "click.shell_complete.CompletionItem",
    minversion="8.0.0",
    reason="click-v8 built-in shell complete is not available, so skipped",
) as CompletionItem:

    def test_shell_complete_arg_v8_func_type():
        def shell_complete_func(ctx, param, incomplete):
            return [
                CompletionItem(name)
                for name in ("foo", "bar")
                if name.startswith(incomplete)
            ]

        @root_command.command()
        @click.argument("handler", shell_complete=shell_complete_func)
        def autocompletion_cmd2(handler):
            pass

        completions = list(c.get_completions(Document("autocompletion-cmd2 ")))
        assert {x.text for x in completions} == {"foo", "bar"}


@pytest.mark.skipif(
    click.__version__[0] < "8",
    reason="click-v8 built-in shell complete is not available, so skipped",
)
def test_tuple_return_type_shell_complete_func():
    def return_type_tuple_shell_complete(ctx, param, incomplete):
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
    @click.argument("foo", shell_complete=return_type_tuple_shell_complete)
    def tuple_type_autocompletion_cmd(foo):
        pass

    completions = list(c.get_completions(Document("tuple-type-autocompletion-cmd ")))
    assert {x.text for x in completions} == {"Hi", "Please", "Hey", "Aye"}

    completions = list(c.get_completions(Document("tuple-type-autocompletion-cmd h")))
    assert {x.text for x in completions} == {"Hi", "Hey"} and {
        x.display_meta[0][-1] for x in completions
    } == {"hi", "hey"}
