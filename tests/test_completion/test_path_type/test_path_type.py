import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document
import glob
import ntpath
import pytest


@click.group()
def root_command():
    pass


c = ClickCompleter(root_command)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("path-type-arg ", glob.glob("*")),
        ("path-type-arg tests/", glob.glob("tests/*")),
        ("path-type-arg click_repl/*", []),
        ("path-type-arg click_repl/**", []),
        (
            "path-type-arg tests/testdir/",
            glob.glob("tests/testdir/*"),
        ),
    ],
)
def test_path_type_arg(test_input, expected):
    @root_command.command()
    @click.argument("path", type=click.Path())
    def path_type_arg(path):
        pass

    completions = list(c.get_completions(Document(test_input)))
    assert {x.display[0][1] for x in completions} == set(
        ntpath.basename(i) for i in expected
    )
