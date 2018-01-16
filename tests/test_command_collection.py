
import click
from click_repl import ClickCompleter, _get_available_commands
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

    cmd_collection = click.CommandCollection(sources=[foo_group, foobar_group])

    cmds = _get_available_commands(cmd_collection)

    assert set(cmds.keys()) == set([
        u'foo_cmd',
        u'foobar_cmd'
    ])
