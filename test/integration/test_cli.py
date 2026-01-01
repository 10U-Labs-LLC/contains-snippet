"""Integration tests for the CLI module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from contains_snippet.cli import main


def run_main_with_args(args: list[str]) -> int:
    """Run main() with patched sys.argv and return exit code."""
    with patch("sys.argv", ["prog"] + args):
        with pytest.raises(SystemExit) as exc_info:
            main()
        return int(exc_info.value.code or 0)


@pytest.mark.integration
class TestMainFunction:
    """Tests for the main() function."""

    def test_snippet_found_exits_0(self, tmp_path: Path) -> None:
        """Exit 0 when snippet is found."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "t.md").write_text("hello world")
        code = run_main_with_args(
            ["--content-file", str(tmp_path / "s.txt"), str(tmp_path / "t.md")]
        )
        assert code == 0

    def test_snippet_missing_exits_1(self, tmp_path: Path) -> None:
        """Exit 1 when snippet is not found."""
        (tmp_path / "s.txt").write_text("missing")
        (tmp_path / "t.md").write_text("hello world")
        code = run_main_with_args(
            ["--content-file", str(tmp_path / "s.txt"), str(tmp_path / "t.md")]
        )
        assert code == 1

    def test_missing_content_file_arg_exits_2(self) -> None:
        """Exit 2 when --content-file is missing."""
        assert run_main_with_args(["somefile.md"]) == 2

    def test_missing_target_files_exits_2(self, tmp_path: Path) -> None:
        """Exit 2 when no target files provided."""
        (tmp_path / "s.txt").write_text("hello")
        assert run_main_with_args(["--content-file", str(tmp_path / "s.txt")]) == 2

    def test_unreadable_content_file_exits_2(self, tmp_path: Path) -> None:
        """Exit 2 when content file cannot be read."""
        (tmp_path / "t.md").write_text("content")
        code = run_main_with_args(
            ["--content-file", "/nonexistent/file.txt", str(tmp_path / "t.md")]
        )
        assert code == 2

    def test_unreadable_target_file_exits_2(self, tmp_path: Path) -> None:
        """Exit 2 when target file cannot be read."""
        (tmp_path / "s.txt").write_text("hello")
        code = run_main_with_args(
            ["--content-file", str(tmp_path / "s.txt"), "/nonexistent/file.md"]
        )
        assert code == 2

    def test_comment_prefix_flag(self, tmp_path: Path) -> None:
        """--comment-prefix forces commented matching."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "t.md").write_text("# hello")
        code = run_main_with_args([
            "--content-file", str(tmp_path / "s.txt"),
            "--comment-prefix", "#",
            str(tmp_path / "t.md"),
        ])
        assert code == 0

    def test_infer_comment_prefix_flag(self, tmp_path: Path) -> None:
        """--infer-comment-prefix uses extension-based matching."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "t.py").write_text("# hello")
        code = run_main_with_args([
            "--content-file", str(tmp_path / "s.txt"),
            "--infer-comment-prefix",
            str(tmp_path / "t.py"),
        ])
        assert code == 0

    def test_comment_prefix_map_flag(self, tmp_path: Path) -> None:
        """--comment-prefix-map overrides extension mapping."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "t.js").write_text("// hello")
        code = run_main_with_args([
            "--content-file", str(tmp_path / "s.txt"),
            "--infer-comment-prefix",
            "--comment-prefix-map", ".js=//",
            str(tmp_path / "t.js"),
        ])
        assert code == 0

    def test_multiple_files_all_match(self, tmp_path: Path) -> None:
        """Exit 0 when all files match."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "f1.md").write_text("hello")
        (tmp_path / "f2.md").write_text("hello world")
        code = run_main_with_args([
            "--content-file", str(tmp_path / "s.txt"),
            str(tmp_path / "f1.md"),
            str(tmp_path / "f2.md"),
        ])
        assert code == 0

    def test_multiple_files_one_missing(self, tmp_path: Path) -> None:
        """Exit 1 when one file is missing the snippet."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "f1.md").write_text("hello")
        (tmp_path / "f2.md").write_text("goodbye")
        code = run_main_with_args([
            "--content-file", str(tmp_path / "s.txt"),
            str(tmp_path / "f1.md"),
            str(tmp_path / "f2.md"),
        ])
        assert code == 1

    def test_help_exits_0(self) -> None:
        """--help exits with code 0."""
        assert run_main_with_args(["--help"]) == 0
