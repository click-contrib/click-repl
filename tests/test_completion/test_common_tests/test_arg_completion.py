import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document


@click.group()
def root_command():
    pass


c = ClickCompleter(root_command, click.Context(root_command))


def test_boolean_arg():
    @root_command.command()
    @click.argument("foo", type=click.BOOL)
    def bool_arg(foo):
        pass

    completions = list(c.get_completions(Document("bool-arg ")))
    assert {x.text for x in completions} == {"true", "false"}

    completions = list(c.get_completions(Document("bool-arg t")))
    assert {x.text for x in completions} == {"true"}


def test_arg_choices():
    @root_command.command()
    @click.argument("handler", type=click.Choice(("foo", "bar")))
    def arg_choices(handler):
        pass

    completions = list(c.get_completions(Document("arg-choices ")))
    assert {x.text for x in completions} == {"foo", "bar"}


def test_only_unused_with_arg():
    @root_command.command()
    @click.argument("handler", type=click.Choice(("foo", "bar")))
    def unused_arg(handler):
        pass

    c.show_only_unused = True

    completions = list(c.get_completions(Document("unused-arg ")))
    assert {x.text for x in completions} == {"foo", "bar"}

    completions = list(c.get_completions(Document("unused-arg foo ")))
    assert {x.text for x in completions} == set()

    c.show_only_unused = False

    completions = list(c.get_completions(Document("unused-arg foo ")))
    assert {x.text for x in completions} == {"foo", "bar"}


def test_only_unused_with_variadic_arg():
    @root_command.command()
    @click.argument("handlers", type=click.Choice(("foo", "bar")), nargs=-1)
    def unused_variadic_arg(handlers):
        pass

    c.show_only_unused = True

    completions = list(c.get_completions(Document("unused-variadic-arg foo ")))
    assert {x.text for x in completions} == {"foo", "bar"}

    c.show_only_unused = False
