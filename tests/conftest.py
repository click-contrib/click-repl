import click_repl
import pytest


@pytest.fixture(scope="session")
def send_stdin_input(monkeypatch):
    iterator = iter((":exit", ":quit", ":q", ":help", ":h", ":?"))

    def fake_stdin(*args):
        return next(iterator)

    click_repl.utils._get_command_func = fake_stdin
