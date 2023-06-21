import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document


@click.group()
def root_command():
    pass


c = ClickCompleter(root_command, click.Context(root_command))


def test_option_choices():
    @root_command.command()
    @click.option("--handler", type=click.Choice(("foo", "bar")))
    def option_choices(handler):
        pass

    completions = list(c.get_completions(Document("option-choices --handler ")))
    assert {x.text for x in completions} == {"foo", "bar"}


def test_boolean_option():
    @root_command.command()
    @click.option("--foo", type=click.BOOL)
    def bool_option(foo):
        pass

    completions = list(c.get_completions(Document("bool-option --foo ")))
    assert {x.text for x in completions} == {"true", "false"}

    completions = list(c.get_completions(Document("bool-option --foo t")))
    assert {x.text for x in completions} == {"true"}


def test_unique_option():
    @root_command.command()
    @click.option("-u", type=click.BOOL)
    def bool_option(foo):
        pass

    completions = list(c.get_completions(Document("bool-option ")))
    assert {x.text for x in completions} == {"-u"}

    completions = list(c.get_completions(Document("bool-option -u t ")))
    assert len(completions) == 0


def test_multiple_option():
    @root_command.command()
    @click.option("-u", type=click.BOOL, multiple=True)
    def bool_option(foo):
        pass

    completions = list(c.get_completions(Document("bool-option ")))
    assert {x.text for x in completions} == {"-u"}

    completions = list(c.get_completions(Document("bool-option -u t ")))
    assert {x.text for x in completions} == {"-u"}
