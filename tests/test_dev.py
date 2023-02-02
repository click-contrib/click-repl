# Test for dev-only functions

from click_repl import utils, exceptions
import pytest


def test_register_cmd_from_str():
    utils._register_internal_command(
        "help", utils._help_internal, "temporary internal help command"
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
        utils._register_internal_command(*test_input)


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("help", utils._help_internal),
        ("h", utils._help_internal),
        ("?", utils._help_internal),
    ],
)
def test_get_registered_target_help_cmd(test_input, expected):
    assert utils._get_registered_target(test_input) == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("exit", utils._exit_internal),
        ("quit", utils._exit_internal),
        ("q", utils._exit_internal),
    ],
)
def test_get_registered_target_exit_cmd(test_input, expected):
    assert utils._get_registered_target(test_input) == expected
    with pytest.raises(exceptions.ExitReplException):
        expected()


@pytest.mark.parametrize("test_input", ["hi", "hello", "76q358767"])
def test_get_registered_target(test_input):
    assert utils._get_registered_target(test_input, "Not Found") == "Not Found"


@pytest.mark.parametrize("test_input", [":help", ":h", ":?"])
def test_internal_help_commands(capsys, test_input):
    utils._exec_internal_and_sys_commands(test_input, allow_internal_commands=True)

    captured_stdout = capsys.readouterr().out

    assert (
        captured_stdout
        == """REPL help:

  External Commands:
    prefix external commands with "!"

  Internal Commands:
    prefix internal commands with ":"
    :exit, :q, :quit  exits the repl
    :?, :h            displays general help information
    :help             temporary internal help command

"""
    )


@pytest.mark.parametrize("test_input", [":exit", ":quit", ":q"])
def test_internal_exit_commands(test_input):
    with pytest.raises(exceptions.ExitReplException):
        utils._exec_internal_and_sys_commands(test_input)


@pytest.mark.parametrize(
    "test_input, expected",
    [("!echo hi", "hi\n"), ("!echo hi hi", "hi hi\n"), ("!", "")],
)
def test_system_commands(capfd, test_input, expected):
    utils._exec_internal_and_sys_commands(test_input)

    captured_stdout = capfd.readouterr().out.replace("\r\n", "\n")
    assert captured_stdout == expected


@pytest.mark.parametrize("test_input", [":exit", ":quit", ":q"])
def test_no_internal_commands(capfd, test_input):
    utils._exec_internal_and_sys_commands(test_input, allow_internal_commands=False)

    captured_stdout = capfd.readouterr().out.replace("\r\n", "\n")

    assert captured_stdout == ""


# f'''Usage: pytest  [OPTIONS] COMMAND [ARGS]...
# Try 'pytest  --help' for help.

# Error: No such command '{test_input}'.
# '''


@pytest.mark.parametrize(
    "test_input",
    ["!echo hi", "!echo hi hi", "!"],
)
def test_no_system_commands(capfd, test_input):
    utils._exec_internal_and_sys_commands(test_input, allow_system_commands=False)

    captured_stdout = capfd.readouterr().out.replace("\r\n", "\n")

    assert captured_stdout == ""


# f'''Usage: pytest  [OPTIONS] COMMAND [ARGS]...
# Try 'pytest  --help' for help.

# Error: No such command '{test_input}'.
# '''


def test_exit_repl_function():
    with pytest.raises(exceptions.ExitReplException):
        utils.exit()
