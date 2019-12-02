==========
click-repl
==========

.. image:: https://travis-ci.org/click-contrib/click-repl.svg?branch=master
    :target: https://travis-ci.org/click-contrib/click-repl

In your click_ app:

.. code:: python

    import click
    from click_repl import register_repl

    @click.group()
    def cli():
        pass

    @cli.command()
    def hello():
        click.echo("Hello world!")

    register_repl(cli)
    cli()

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
* ``!``-prefix executes shell commands.

You can use the internal ``:help`` command to explain usage.

PyPI: `<https://pypi.python.org/pypi/click-repl>`_

.. _click: http://click.pocoo.org/

Advanced Usage
==============

For more flexibility over how your REPL works you can use the ``repl`` function
directly instead of ``register_repl``. For example, in your app:

.. code:: python

    import click
    from click_repl import repl
    from prompt_toolkit.history import FileHistory

    @click.group()
    def cli():
        pass

    @cli.command()
    def myrepl():
        prompt_kwargs = {
            'history': FileHistory('/etc/myrepl/myrepl-history'),
        }
        repl(click.get_current_context(), prompt_kwargs=prompt_kwargs)
        
    cli()

And then your custom ``myrepl`` command will be available on your CLI, which
will start a REPL which has its history stored in
``/etc/myrepl/myrepl-history`` and persist between sessions.

Any arguments that can be passed to the ``python-prompt-toolkit`` Prompt_ class
can be passed in the ``prompt_kwargs`` argument and will be used when
instantiating your ``Prompt``.

.. _Prompt: http://python-prompt-toolkit.readthedocs.io/en/stable/pages/reference.html?prompt_toolkit.shortcuts.Prompt#prompt_toolkit.shortcuts.Prompt

this is a more advanced example

.. code:: python

    import os
    from pathlib import Path

    import click
    from click_repl import repl
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.history import FileHistory


    history_file_path = os.path.join(Path.home(), ".click_history")
    # don't truncate file with `w+`, it's a history file for God's sake
    with open(history_file_path, "a+"):
        pass

    @click.group(invoke_without_command=True)
    @click.pass_context
    def main(ctx):
        if not ctx.invoked_subcommand:
            prompt_kwargs = {
                "history": FileHistory(history_file_path),
                "complete_while_typing": True,
                "auto_suggest": AutoSuggestFromHistory(),
                "validate_while_typing": True,
                "enable_history_search": True,
                "message": "> ",
            }
            repl(click.get_current_context(), prompt_kwargs=prompt_kwargs)

    @main.group()
    def root_command():
        pass

    main()

License
=======

Licensed under the MIT, see ``LICENSE``.
