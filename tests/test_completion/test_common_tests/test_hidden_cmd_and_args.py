import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document


@click.group()
def root_command():
    pass


c = ClickCompleter(root_command, click.Context(root_command))


def test_hidden_cmd():
    @root_command.command(hidden=True)
    @click.option("--handler", "-h")
    def hidden_cmd(handler):
        pass

    completions = list(c.get_completions(Document("hidden-")))
    assert {x.text for x in completions} == set()


def test_hidden_option():
    @root_command.command()
    @click.option("--handler", "-h", hidden=True)
    def hidden_option_cmd(handler):
        pass

    completions = list(c.get_completions(Document("hidden-option-cmd ")))
    assert {x.text for x in completions} == set()


def test_args_of_hidden_command():
    @root_command.command(hidden=True)
    @click.argument("handler1", type=click.Choice(("foo", "bar")))
    @click.option("--handler2", type=click.Choice(("foo", "bar")))
    def args_choices_hidden_cmd(handler):
        pass

    completions = list(c.get_completions(Document("option-")))
    assert {x.text for x in completions} == set()

    completions = list(c.get_completions(Document("args-choices-hidden-cmd foo ")))
    assert {x.text for x in completions} == set()

    completions = list(
        c.get_completions(Document("args-choices-hidden-cmd --handler "))
    )
    assert {x.text for x in completions} == set()


def test_completion_multilevel_command():
    @click.group()
    def root_group():
        pass

    @root_group.group()
    def first_level_command():
        pass

    @first_level_command.command()
    def second_level_command_one():
        pass

    @first_level_command.command()
    def second_level_command_two():
        pass

    c = ClickCompleter(root_group, click.Context(root_group))

    completions = list(c.get_completions(Document("first-level-command ")))
    assert set(x.text for x in completions) == {
        "second-level-command-one",
        "second-level-command-two",
    }

    completions = list(c.get_completions(Document(" ")))
    assert {x.text for x in completions} == {"first-level-command"}
