"""Unit tests for the __main__ module."""

import runpy
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.mark.unit
def test_main_module_calls_main(tmp_path: Path) -> None:
    """Running as __main__ calls the main function."""
    snippet_file = tmp_path / "snippet.txt"
    snippet_file.write_text("content")
    target_file = tmp_path / "target.md"
    target_file.write_text("content")

    with patch("sys.argv", ["prog", "--snippet-file", str(snippet_file), str(target_file)]):
        with pytest.raises(SystemExit) as exc_info:
            runpy.run_module("contains_snippet", run_name="__main__")
        assert exc_info.value.code == 0
