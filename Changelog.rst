.. _changelog:

================
 Change history
================

.. _version-0.4.0:

0.4.0
======
:release-date: 17 Sep, 2026
:release-by: Asif Saif Uddin

- Hide already used (non-multiple) options (#104)
- Fix values shown for wrong option (#106)
- Add a shortest_only option (#105)
- Unhandled exception during autocomplete fix (#109)
- Added ReplContext class (#118)
- Support python 3.13, limit click version
- Update tox.ini to remove Python 3.8 and change mypy version (#134)
- Compatibility with click 8.2+ (#132)
- Do not offer true/false value completions for boolean flags (``is_flag=True``,
  including ``--foo/--no-foo`` style options), which previously inserted a value
  into the positional-argument slot (#116).
- ``show_only_unused`` now also applies to arguments, so an argument that has
  already been given is no longer completed again (#125).
-Fix shortest-only completion at an empty root prompt - #138


.. _version-0.3.0:

0.3.0
=====
:release-date: 15 Jun, 2023
:release-by: Asif Saif Uddin

- Drop Python 2 support, remove six.
- Uses PromptSession() class from prompt_toolkit instead of prompt() function (#63).
- Added filter for hidden commands and options (#86).
- Added click's autocompletion support (#88).
- Added tab-completion for Path and BOOL type arguments (#95).
- Added 'expand environmental variables in path' feature (#96).
- Delegate command dispatching to the actual group command.
- Updated completer class and tests based on new fix#92 (#102).
- Python 3.11 support.



.. _version-0.2.0:

0.2.0
=====
:release-date: 31 May, 2021
:release-by: untitaker

- Backwards compatibility between click 7 & 8
- support for click 8 changes
- Update tests to expect hyphens