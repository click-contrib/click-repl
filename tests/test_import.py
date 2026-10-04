"""Importing the package must work without an attached standard input."""

import os
import subprocess
import sys


def test_import_without_stdin():
    # Closing fd 0 causes Python to expose sys.stdin as None. Test in a
    # child so the test runner's own input stream remains untouched.
    if os.name == "nt":
        code = "import sys; sys.stdin = None; import click_repl"
        result = subprocess.run([sys.executable, "-c", code], capture_output=True)
    else:
        result = subprocess.run(
            [sys.executable, "-c", "import sys; assert sys.stdin is None; "
             "import click_repl"],
            capture_output=True,
            preexec_fn=lambda: os.close(0),
        )
    assert result.returncode == 0, result.stderr.decode(errors="replace")
