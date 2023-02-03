import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document


@click.group()
def root_command():
    pass


def test_completion():
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


def test_hidden_command():
    @root_command.command(hidden=True)
    @click.option("--handler", "-h")
    def hidden_cmd(handler):
        pass

    c = ClickCompleter(root_command)
    completions = list(c.get_completions(Document("hidden")))
    assert set(x.text for x in completions) == set()


def test_hidden_option():
    @root_command.command()
    @click.option("--handler", "-h", hidden=True)
    def hidden_cmd(handler):
        pass

    c = ClickCompleter(root_command)
    completions = list(c.get_completions(Document("hidden-cmd ")))
    assert set(x.text for x in completions) == set()
