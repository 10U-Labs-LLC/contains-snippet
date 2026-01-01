"""Integration tests for the __main__ module."""

import importlib
from unittest.mock import patch

import pytest


@pytest.mark.integration
def test_main_module_invokes_cli(tmp_path: pytest.TempPathFactory) -> None:
    """Importing __main__ calls the main function."""
    snippet = tmp_path / "s.txt"  # type: ignore[operator]
    snippet.write_text("x")
    target = tmp_path / "t.md"  # type: ignore[operator]
    target.write_text("x")

    with patch("sys.argv", ["prog", "--content-file", str(snippet), str(target)]):
        with pytest.raises(SystemExit) as exc_info:
            import contains_snippet.__main__  # pylint: disable=import-outside-toplevel
            importlib.reload(contains_snippet.__main__)
        assert exc_info.value.code == 0
