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
    completions = list(c.get_completions(Document("first-level-command ")))

    assert set(x.text for x in completions) == set(
        ["second-level-command-one", "second-level-command-two"]
    )

    c = ClickCompleter(root_command)
    completions = list(c.get_completions(Document(" ")))

    assert set(x.text for x in completions) == set(
        ["first-level-command"]
    )
