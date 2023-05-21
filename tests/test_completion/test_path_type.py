import click
from click_repl import ClickCompleter
from prompt_toolkit.document import Document
import os
import glob
import pytest


@click.group()
def root_command():
    pass


c = ClickCompleter(root_command, click.Context(root_command))


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("path-type-arg ", glob.glob("*")),
        ("path-type-arg tests/", glob.glob("tests/*")),
        ("path-type-arg src/*", []),
        ("path-type-arg src/**", []),
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
    assert {x.display[0][1] for x in completions} == {
        os.path.basename(i) for i in expected
    }


# @pytest.mark.skipif(os.name != 'nt', reason='This is a test for Windows OS')
# def test_win_path_env_expanders():
#     completions = list(c.get_completions(Document('path-type-arg %LocalAppData%')))
#     assert {x.display[0][1] for x in completions} == {'Local', 'LocalLow'}
