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

    def test_shell_complete_option_v8_class_type():
        class MyVar(click.ParamType):
            name = "myvar"

            def shell_complete(self, ctx, param, incomplete):
                return [
                    CompletionItem(name)
                    for name in ("foo", "bar")
                    if name.startswith(incomplete)
                ]

        @root_command.command()
        @click.option("--handler", "-h", type=MyVar())
        def autocompletion_opt_cmd(handler):
            pass

        completions = list(c.get_completions(Document("autocompletion-opt-cmd ")))
        assert {x.text for x in completions} == {"--handler", "bar"}


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
        @click.option("--handler", "-h", shell_complete=shell_complete_func)
        def autocompletion_cmd2(handler):
            pass

        completions = list(
            c.get_completions(Document("autocompletion-cmd2 --handler "))
        )
        assert {x.text for x in completions} == {"foo", "bar"}

        completions = list(
            c.get_completions(Document("autocompletion-cmd2 --handler "))
        )
        assert {x.text for x in completions} == {"foo", "bar"}
