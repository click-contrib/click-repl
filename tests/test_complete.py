import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document
import pytest


@click.group()
def root_command():
    pass


c = ClickCompleter(root_command)

with pytest.importorskip(
    "click.shell_complete.CompletionItem",
    minversion="8.0.0",
    reason="click's built-in shell complete is not available, so skipped",
) as CompletionItem:

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
    assert set(x.text for x in completions) == set(("foo", "bar"))

    @root_command.command()
    @click.argument("--handler", "-h", type=MyVar())
    def autocompletion_opt_cmd(handler):
        pass

    completions = list(c.get_completions(Document("autocompletion-cmd ")))
    assert set(x.text for x in completions) == set(("--handler", "bar"))


with pytest.importorskip(
    "click.shell_complete.CompletionItem",
    minversion="8.0.0",
    reason="click-v8 built-in shell complete is not available, so skipped",
) as CompletionItem:

    def shell_complete_func(self, ctx, param, incomplete):
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
    assert set(x.text for x in completions) == set(("foo", "bar"))


@pytest.mark.skipif(
    click.__version__[0] != "7",
    reason="click-v7 old autocomplete module is not available, so skipped",
)
def test_click7_autoocmplete_arg():
    def shell_complete_func(self, ctx, param, incomplete):
        return [name for name in ("foo", "bar") if name.startswith(incomplete)]

    @root_command.command()
    @click.argument("handler", autocompletion=shell_complete_func)
    def autocompletion_cmd2(handler):
        pass

    completions = list(c.get_completions(Document("autocompletion-cmd2 ")))
    assert set(x.text for x in completions) == set(("foo", "bar"))
