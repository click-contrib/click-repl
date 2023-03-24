import click_repl
import pytest


@pytest.mark.parametrize(
    "test_input, expected",
    [("!echo hi", "hi\n"), ("!echo hi hi", "hi hi\n"), ("!", "")],
)
def test_system_commands(capfd, test_input, expected):
    click_repl.utils._execute_internal_and_sys_cmds(test_input)

    captured_stdout = capfd.readouterr().out.replace("\r\n", "\n")
    assert captured_stdout == expected


@pytest.mark.parametrize(
    "test_input",
    ["!echo hi", "!echo hi hi", "!"],
)
def test_no_system_commands(capfd, test_input):
    click_repl.utils._execute_internal_and_sys_cmds(
        test_input, allow_system_commands=False
    )

    captured_stdout = capfd.readouterr().out.replace("\r\n", "\n")
    assert captured_stdout == ""
