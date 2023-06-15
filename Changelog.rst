.. _changelog:

================
 Change history
================

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