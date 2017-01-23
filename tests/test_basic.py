import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document


def test_completion():
    @click.group()
    def root_command():
        pass

    @root_command.group()
    def first_level_command():
        pass

    @first_level_command.command()
    def second_level_command_one():
        pass

    @first_level_command.command()
    def second_level_command_two():
        pass

    c = ClickCompleter(root_command)
    completions = list(c.get_completions(Document(u'first_level_command ')))

    assert set(x.text for x in completions) == set([
        u'second_level_command_one',
        u'second_level_command_two'
    ])
