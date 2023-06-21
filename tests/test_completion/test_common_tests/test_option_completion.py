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
    @click.option("--wrong", type=click.Choice(("bogged", "bogus")))
    def option_choices(handler):
        pass

    completions = list(c.get_completions(Document("option-choices --handler ")))
    assert {x.text for x in completions} == {"foo", "bar"}

    completions = list(c.get_completions(Document("option-choices --wrong ")))
    assert {x.text for x in completions} == {"bogged", "bogus"}


def test_boolean_option():
    @root_command.command()
    @click.option("--foo", type=click.BOOL)
    def bool_option(foo):
        pass

    completions = list(c.get_completions(Document("bool-option --foo ")))
    assert {x.text for x in completions} == {"true", "false"}

    completions = list(c.get_completions(Document("bool-option --foo t")))
    assert {x.text for x in completions} == {"true"}


def test_only_unused_with_unique_option():
    @root_command.command()
    @click.option("-u", type=click.BOOL)
    def unique_option(u):
        pass

    c.show_only_unused = True

    completions = list(c.get_completions(Document("unique-option ")))
    assert {x.text for x in completions} == {"-u"}

    completions = list(c.get_completions(Document("unique-option -u t ")))
    assert len(completions) == 0

    c.show_only_unused = False

    completions = list(c.get_completions(Document("unique-option -u t ")))
    assert {x.text for x in completions} == {"-u"}


def test_only_unused_with_multiple_option():
    @root_command.command()
    @click.option("-u", type=click.BOOL, multiple=True)
    def multiple_option(u):
        pass

    c.show_only_unused = True

    completions = list(c.get_completions(Document("multiple-option ")))
    assert {x.text for x in completions} == {"-u"}

    completions = list(c.get_completions(Document("multiple-option -u t ")))
    assert {x.text for x in completions} == {"-u"}

    c.show_only_unused = False

    completions = list(c.get_completions(Document("multiple-option -u t ")))
    assert {x.text for x in completions} == {"-u"}


def test_shortest_only_mode():
    @root_command.command()
    @click.option("--foo", "-f", is_flag=True)
    @click.option("-b", "--bar", is_flag=True)
    @click.option("--foobar", is_flag=True)
    def shortest_only(foo, bar, foobar):
        pass

    c.shortest_only = True

    completions = list(c.get_completions(Document("shortest-only ")))
    assert {x.text for x in completions} == {"-f", "-b", "--foobar"}

    completions = list(c.get_completions(Document("shortest-only -")))
    assert {x.text for x in completions} == {"-f", "--foo", "-b", "--bar", "--foobar"}

    completions = list(c.get_completions(Document("shortest-only --f")))
    assert {x.text for x in completions} == {"--foo", "--foobar"}

    c.shortest_only = False

    completions = list(c.get_completions(Document("shortest-only ")))
    assert {x.text for x in completions} == {"-f", "--foo", "-b", "--bar", "--foobar"}
