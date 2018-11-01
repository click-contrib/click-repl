import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document


def test_completion():
    @click.group()
    def root_command():
        pass

    @root_command.command()
    @click.argument("handler", type=click.Choice(["foo", "bar"]))
    def arg_cmd():
        pass

    c = ClickCompleter(root_command)
    completions = list(c.get_completions(Document(u"arg-cmd ")))

    assert set(x.text for x in completions) == set([u"foo", u"bar"])
