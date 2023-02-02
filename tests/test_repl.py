import click
from click_repl import register_repl
import pytest


def test_repl():
    @click.group()
    def cli():
        pass


    @cli.command()
    @click.option("--baz", is_flag=True)
    def foo(baz):
        print("Foo!")


    @cli.command()
    @click.option("--foo", is_flag=True)
    def bar(foo):
        print("Bar!")


    register_repl(cli)

    with pytest.raises(SystemExit):
        cli()
