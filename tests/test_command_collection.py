
import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document


def test_completion():
    @click.group()
    def foo_group():
        pass

    @foo_group.command()
    def foo_cmd():
        pass

    @click.group()
    def foobar_group():
        pass

    @foobar_group.command()
    def foobar_cmd():
        pass

    c = ClickCompleter(click.CommandCollection(sources=[foo_group, foobar_group]))
    completions = list(c.get_completions(Document(u"foo")))

    assert set(x.text for x in completions) == set([u"foo-cmd", u"foobar-cmd"])
