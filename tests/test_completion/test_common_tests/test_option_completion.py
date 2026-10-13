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


def test_flag_option_offers_no_value():
    # A flag (is_flag=True) does not consume a value, so once it has been
    # typed the completer must not offer true/false as if it needed one.
    # It must, however, keep completing the command's other parameters
    # instead of stopping.
    # See https://github.com/click-contrib/click-repl/issues/116
    @root_command.command()
    @click.argument("arg1", type=click.Choice(("alpha", "beta")))
    @click.option("-b", "--some-option", "some_option", is_flag=True)
    def flag_option(arg1, some_option):
        pass

    completions = {x.text for x in c.get_completions(Document("flag-option -b "))}
    # No true/false value completion for the flag itself.
    assert "true" not in completions and "false" not in completions
    # Remaining argument still completes.
    assert {"alpha", "beta"} <= completions

    completions = {x.text for x in c.get_completions(Document("flag-option --some-option "))}
    assert "true" not in completions and "false" not in completions
    assert {"alpha", "beta"} <= completions


def test_boolean_flag_with_secondary_opts_offers_no_value():
    # Flags declared with a secondary option (--foo/--no-foo) are also flags
    # and must not trigger true/false value completions, while still letting
    # the remaining parameters complete.
    @root_command.command()
    @click.argument("arg1", type=click.Choice(("alpha", "beta")))
    @click.option("--shout/--no-shout", default=False)
    def toggle_flag(arg1, shout):
        pass

    completions = {x.text for x in c.get_completions(Document("toggle-flag --shout "))}
    assert "true" not in completions and "false" not in completions
    assert {"alpha", "beta"} <= completions

    completions = {x.text for x in c.get_completions(Document("toggle-flag --no-shout "))}
    assert "true" not in completions and "false" not in completions
    assert {"alpha", "beta"} <= completions


def test_completion_continues_after_boolean_flag():
    # A flag consumes no value, so after it has been typed the completer must
    # still offer the command's remaining options and arguments instead of
    # stopping. See https://github.com/click-contrib/click-repl/issues/116
    @root_command.command()
    @click.argument("arg1", type=click.Choice(("foo", "bar")))
    @click.option("--verbose", is_flag=True)
    @click.option("--mode", type=click.Choice(("fast", "slow")))
    def continue_after_flag(arg1, verbose, mode):
        pass

    # Remaining options are still offered after the flag.
    completions = list(c.get_completions(Document("continue-after-flag --verbose --")))
    assert {x.text for x in completions} >= {"--verbose", "--mode"}

    # The positional argument still completes after the flag.
    completions = list(c.get_completions(Document("continue-after-flag --verbose ")))
    assert {"foo", "bar"} <= {x.text for x in completions}

    # Still works after more than one flag.
    completions = list(c.get_completions(Document("continue-after-flag --verbose ba")))
    assert {x.text for x in completions} == {"bar"}


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


def test_shortest_only_at_empty_root_prompt(capsys):
    @click.group()
    @click.option("--verbose", "-v", is_flag=True)
    def root(verbose):
        pass

    @root.command()
    def child():
        pass

    completer = ClickCompleter(root, click.Context(root), shortest_only=True)
    completions = list(completer.get_completions(Document("")))
    assert {item.text for item in completions} == {"-v", "child"}
    assert capsys.readouterr().out == ""
