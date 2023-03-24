import click_repl
import pytest


@pytest.mark.parametrize("test_input", [":help", ":h", ":?"])
def test_internal_help_commands(capsys, test_input):
    click_repl.utils._execute_internal_and_sys_cmds(
        test_input, allow_internal_commands=True
    )

    captured_stdout = capsys.readouterr().out

    assert (
        captured_stdout
        == """REPL help:

  External Commands:
    prefix external commands with "!"

  Internal Commands:
    prefix internal commands with ":"
    :exit, :q, :quit  exits the repl
    :?, :h, :help     displays general help information

"""
    )


@pytest.mark.parametrize("test_input", [":exit", ":quit", ":q"])
def test_internal_exit_commands(test_input):
    with pytest.raises(click_repl.exceptions.ExitReplException):
        click_repl.utils._execute_internal_and_sys_cmds(test_input)


@pytest.mark.parametrize("test_input", [":exit", ":quit", ":q"])
def test_no_internal_commands(capfd, test_input):
    click_repl.utils._execute_internal_and_sys_cmds(
        test_input, allow_internal_commands=False
    )

    captured_stdout = capfd.readouterr().out.replace("\r\n", "\n")
    assert captured_stdout == ""
