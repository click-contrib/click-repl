import click
from click_repl import register_repl


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

if __name__ == "__main__":
    cli()
