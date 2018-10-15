import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document


def test_completion_with_argument():
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

def test_completion_with_option():
    @click.group()
    def root_command():
        pass

    @root_command.command()
    @click.option("--handler-1", type=click.Choice(["foo", "bar"]))
    @click.option("--handler-2", type=click.Choice(["foo", "bar"]))
    def arg_cmd():
        pass

    c = ClickCompleter(root_command)
    completions = list(c.get_completions(Document(u"arg-cmd ")))

    assert set(x.text for x in completions) == set([u"--handler-1", u"--handler-2"])

def test_completion_wont_show_hidden_groups():

    @click.group()
    def main():
        pass

    @main.group()
    def root_command_1():
        pass

    @root_command_1.command()
    @click.option("--handler", type=click.Choice(["foo", "bar"]))
    def arg_cmd_1():
        pass

    @main.group(hidden=True)
    def root_command_2():
        pass

    @root_command_2.command()
    @click.option("--handler", type=click.Choice(["foo", "bar"]))
    def arg_cmd_2():
        pass


    c = ClickCompleter(main)
    completions = list(c.get_completions(Document(u" ")))

    assert set(x.text for x in completions) == set([u"root-command-1"])


def test_completion_wont_show_already_typed_options():

    @click.group()
    def root_command():
        pass

    @root_command.command()
    @click.option("--handler-1", type=click.Choice(["foo", "bar"]))
    @click.option("--handler-2", type=click.Choice(["foo", "bar"]))
    def arg_cmd():
        pass

    c = ClickCompleter(root_command)
    completions = list(c.get_completions(Document(u"arg-cmd --handler-1 foo ")))

    assert set(x.text for x in completions) == set([u"--handler-2"])

