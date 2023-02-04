import click_repl
import pytest


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("help", click_repl.utils._help_internal),
        ("h", click_repl.utils._help_internal),
        ("?", click_repl.utils._help_internal),
    ],
)
def test_get_registered_target_help_cmd(test_input, expected):
    assert click_repl.utils._get_registered_target(test_input) == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("exit", click_repl.utils._exit_internal),
        ("quit", click_repl.utils._exit_internal),
        ("q", click_repl.utils._exit_internal),
    ],
)
def test_get_registered_target_exit_cmd(test_input, expected):
    assert click_repl.utils._get_registered_target(test_input) == expected
    with pytest.raises(click_repl.exceptions.ExitReplException):
        expected()


@pytest.mark.parametrize("test_input", ["hi", "hello", "76q358767"])
def test_get_registered_target(test_input):
    assert (
        click_repl.utils._get_registered_target(test_input, "Not Found") == "Not Found"
    )
