"""Integration tests for the __main__ module."""

import runpy
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.mark.integration
def test_main_module_invokes_cli(tmp_path: Path) -> None:
    """Running python -m contains_snippet calls the main function."""
    content_file = tmp_path / "content.txt"
    content_file.write_text("hello")
    check_file = tmp_path / "check.md"
    check_file.write_text("hello")

    argv = ["prog", "--snippet-file", str(content_file), str(check_file)]
    with patch("sys.argv", argv):
        with pytest.raises(SystemExit) as exc:
            runpy.run_module("contains_snippet", run_name="__main__")
        assert exc.value.code == 0
