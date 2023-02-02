import click_repl
import pytest


@pytest.fixture
def send_stdin_input(monkeypatch):
    iterator = iter((":help", ":h", ":?", ":exit"))

    def fake_stdin_provider(*args):
        return lambda: next(iterator)

    monkeypatch.setattr(click_repl.utils, "_get_command_func", fake_stdin_provider)
