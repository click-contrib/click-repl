import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document


def test_completion_with_option_with_various_data_types():
    @click.group()
    def root_command():
        pass

    @root_command.command()
    @click.option("--handler-1", type=click.Choice(["foo", "bar"]))
    @click.option("--handler-2", type=click.Choice([1, 2]))
    @click.option("--handler-3", type=click.Choice([]))
    @click.option("--handler-4", type=int)
    @click.option("--handler-5",)
    def arg_cmd(*args, **kwargs):
        pass

    c = ClickCompleter(root_command)
    completions = list(c.get_completions(Document(u"arg-cmd ")))

    assert set(x.text for x in completions) == set(
        [u"--handler-1", u"--handler-2", u"--handler-3", u"--handler-4", u"--handler-5"]
    )


def test_completion_dont_show_hidden_groups():
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


def test_completion_dont_show_hidden_options():
    @click.group()
    def root_command():
        pass

    @root_command.command()
    @click.option("--handler-1", hidden=True)
    @click.option("--handler-2",)
    def arg_cmd():
        pass

    c = ClickCompleter(root_command)
    completions = list(c.get_completions(Document(u"arg-cmd ")))

    assert set(x.text for x in completions) == set([u"--handler-2"])


def test_completion_dont_show_already_typed_options():
    @click.group()
    def root_command():
        pass

    @root_command.command()
    @click.option("--handler-1", type=click.Choice(["foo", "bar"]))
    @click.option("--handler-2", type=click.Choice([1, 2]))
    def arg_cmd():
        pass

    c = ClickCompleter(root_command)
    completions = list(c.get_completions(Document(u"arg-cmd --handler-1 foo ")))

    assert set(x.text for x in completions) == set([u"--handler-2"])
