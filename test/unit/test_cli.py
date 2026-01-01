"""Unit tests for the CLI module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from contains_snippet.cli import main


@pytest.mark.unit
class TestMainFunction:
    """Tests for the main() function."""

    def test_snippet_found_exits_0(self, tmp_path: Path) -> None:
        """Exit 0 when snippet is found."""
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("hello")
        target_file = tmp_path / "target.md"
        target_file.write_text("hello world")

        with patch("sys.argv", ["prog", "--content-file", str(content_file), str(target_file)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_snippet_missing_exits_1(self, tmp_path: Path) -> None:
        """Exit 1 when snippet is not found."""
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("missing")
        target_file = tmp_path / "target.md"
        target_file.write_text("hello world")

        with patch("sys.argv", ["prog", "--content-file", str(content_file), str(target_file)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_missing_content_file_arg_exits_2(self) -> None:
        """Exit 2 when --content-file is missing."""
        with patch("sys.argv", ["prog", "somefile.md"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    def test_missing_target_files_exits_2(self, tmp_path: Path) -> None:
        """Exit 2 when no target files provided."""
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("hello")

        with patch("sys.argv", ["prog", "--content-file", str(content_file)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    def test_unreadable_content_file_exits_2(self, tmp_path: Path) -> None:
        """Exit 2 when content file cannot be read."""
        target_file = tmp_path / "target.md"
        target_file.write_text("content")

        args = ["prog", "--content-file", "/nonexistent/file.txt", str(target_file)]
        with patch("sys.argv", args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    def test_unreadable_target_file_exits_2(self, tmp_path: Path) -> None:
        """Exit 2 when target file cannot be read."""
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("hello")

        args = ["prog", "--content-file", str(content_file), "/nonexistent/file.md"]
        with patch("sys.argv", args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    def test_comment_prefix_flag(self, tmp_path: Path) -> None:
        """--comment-prefix forces commented matching."""
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("hello")
        target_file = tmp_path / "target.md"
        target_file.write_text("# hello")

        with patch("sys.argv", ["prog", "--content-file", str(content_file),
                                "--comment-prefix", "#", str(target_file)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_infer_comment_prefix_flag(self, tmp_path: Path) -> None:
        """--infer-comment-prefix uses extension-based matching."""
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("hello")
        target_file = tmp_path / "target.py"
        target_file.write_text("# hello")

        with patch("sys.argv", ["prog", "--content-file", str(content_file),
                                "--infer-comment-prefix", str(target_file)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_comment_prefix_map_flag(self, tmp_path: Path) -> None:
        """--comment-prefix-map overrides extension mapping."""
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("hello")
        target_file = tmp_path / "target.js"
        target_file.write_text("// hello")

        with patch("sys.argv", ["prog", "--content-file", str(content_file),
                                "--infer-comment-prefix",
                                "--comment-prefix-map", ".js=//",
                                str(target_file)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_multiple_files_all_match(self, tmp_path: Path) -> None:
        """Exit 0 when all files match."""
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("hello")
        file1 = tmp_path / "file1.md"
        file1.write_text("hello")
        file2 = tmp_path / "file2.md"
        file2.write_text("hello world")

        with patch("sys.argv", ["prog", "--content-file", str(content_file),
                                str(file1), str(file2)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_multiple_files_one_missing(self, tmp_path: Path) -> None:
        """Exit 1 when one file is missing the snippet."""
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("hello")
        file1 = tmp_path / "file1.md"
        file1.write_text("hello")
        file2 = tmp_path / "file2.md"
        file2.write_text("goodbye")

        with patch("sys.argv", ["prog", "--content-file", str(content_file),
                                str(file1), str(file2)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_help_exits_0(self) -> None:
        """--help exits with code 0."""
        with patch("sys.argv", ["prog", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
