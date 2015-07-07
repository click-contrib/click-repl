==========
click-repl
==========

In your click_ app::

    import click
    from click_repl import register_repl

    @click.group()
    def cli():
        pass

    @cli.command()
    def hello():
        click.echo("Hello world!")

    register_repl(cli)

In the shell::

    $ my_app repl
    > hello
    Hello world!
    > ^C
    $ echo hello | my_app repl
    Hello world!

Features not shown:

* Tab-completion.
* The parent context is reused, which means ``ctx.obj`` persists between
  subcommands. If you're keeping caches on that object (like I do), using the
  app's repl instead of the shell is a huge performance win.

.. _click: http://click.pocoo.org/
