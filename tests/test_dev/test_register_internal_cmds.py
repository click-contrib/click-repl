import click_repl
import pytest


def test_register_cmd_from_str():
    click_repl.utils._register_internal_command(
        "help2", click_repl.utils._help_internal, "temporary internal help command"
    )


@pytest.mark.parametrize(
    "test_input",
    [
        ({"h": "help"}, str),
        (["h", "help", "?"], str()),
    ],
)
def test_register_func_xfails(test_input):
    with pytest.raises(ValueError):
        click_repl.utils._register_internal_command(*test_input)
