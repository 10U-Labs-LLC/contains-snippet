"""Unit tests for the CLI module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from contains_snippet.cli import BUILTIN_PREFIX_MAP, main, parse_prefix_map


@pytest.mark.unit
class TestParsePrefixMap:
    """Tests for parse_prefix_map function."""

    def test_single_entry(self) -> None:
        """Parse single extension mapping."""
        result = parse_prefix_map(".js=//")
        assert result == {".js": "//"}

    def test_multiple_entries(self) -> None:
        """Parse multiple extension mappings."""
        result = parse_prefix_map(".js=//,.ts=//,.go=//")
        assert result == {".js": "//", ".ts": "//", ".go": "//"}

    def test_raw_value(self) -> None:
        """'raw' value becomes None."""
        result = parse_prefix_map(".md=raw")
        assert result == {".md": None}

    def test_raw_case_insensitive(self) -> None:
        """'RAW' value also becomes None."""
        result = parse_prefix_map(".md=RAW")
        assert result == {".md": None}

    def test_extension_normalized(self) -> None:
        """Extension is normalized to lowercase."""
        result = parse_prefix_map(".JS=//")
        assert result == {".js": "//"}

    def test_whitespace_stripped(self) -> None:
        """Whitespace around parts is stripped."""
        result = parse_prefix_map(" .js = // ")
        assert result == {".js": "//"}


@pytest.mark.unit
class TestBuiltinPrefixMap:
    """Tests for BUILTIN_PREFIX_MAP constant."""

    def test_md_is_raw(self) -> None:
        """Markdown files use raw matching."""
        assert BUILTIN_PREFIX_MAP[".md"] is None

    def test_py_uses_hash(self) -> None:
        """Python files use hash comment prefix."""
        assert BUILTIN_PREFIX_MAP[".py"] == "#"

    def test_yml_uses_hash(self) -> None:
        """YAML files use hash comment prefix."""
        assert BUILTIN_PREFIX_MAP[".yml"] == "#"

    def test_yaml_uses_hash(self) -> None:
        """YAML files (alt ext) use hash comment prefix."""
        assert BUILTIN_PREFIX_MAP[".yaml"] == "#"


@pytest.mark.unit
class TestMain:
    """Tests for main() function."""

    def test_snippet_found_exits_0(self, tmp_path: Path) -> None:
        """Exit 0 when snippet is found in all files."""
        snippet_file = tmp_path / "snippet.txt"
        snippet_file.write_text("hello")
        target = tmp_path / "target.md"
        target.write_text("hello world")

        with patch("sys.argv", ["prog", "--snippet-file", str(snippet_file), str(target)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_snippet_not_found_exits_1(self, tmp_path: Path) -> None:
        """Exit 1 when snippet is not found."""
        snippet_file = tmp_path / "snippet.txt"
        snippet_file.write_text("missing")
        target = tmp_path / "target.md"
        target.write_text("hello world")

        with patch("sys.argv", ["prog", "--snippet-file", str(snippet_file), str(target)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_missing_snippet_file_arg_exits_2(self) -> None:
        """Exit 2 when --snippet-file argument is missing."""
        with patch("sys.argv", ["prog", "target.md"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    def test_unreadable_snippet_file_exits_2(self, tmp_path: Path) -> None:
        """Exit 2 when snippet file cannot be read."""
        target = tmp_path / "target.md"
        target.write_text("content")

        with patch("sys.argv", ["prog", "--snippet-file", "/nonexistent", str(target)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    def test_unreadable_target_file_exits_2(self, tmp_path: Path) -> None:
        """Exit 2 when target file cannot be read."""
        snippet_file = tmp_path / "snippet.txt"
        snippet_file.write_text("hello")

        with patch("sys.argv", ["prog", "--snippet-file", str(snippet_file), "/nonexistent"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    def test_comment_prefix_flag(self, tmp_path: Path) -> None:
        """--comment-prefix forces commented matching."""
        snippet_file = tmp_path / "snippet.txt"
        snippet_file.write_text("hello")
        target = tmp_path / "target.md"
        target.write_text("# hello")

        with patch("sys.argv", [
            "prog", "--snippet-file", str(snippet_file),
            "--comment-prefix", "#", str(target)
        ]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_infer_comment_prefix_flag(self, tmp_path: Path) -> None:
        """--infer-comment-prefix uses extension mapping."""
        snippet_file = tmp_path / "snippet.txt"
        snippet_file.write_text("hello")
        target = tmp_path / "target.py"
        target.write_text("# hello")

        with patch("sys.argv", [
            "prog", "--snippet-file", str(snippet_file),
            "--infer-comment-prefix", str(target)
        ]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_comment_prefix_map_flag(self, tmp_path: Path) -> None:
        """--comment-prefix-map with --infer-comment-prefix."""
        snippet_file = tmp_path / "snippet.txt"
        snippet_file.write_text("hello")
        target = tmp_path / "target.js"
        target.write_text("// hello")

        with patch("sys.argv", [
            "prog", "--snippet-file", str(snippet_file),
            "--infer-comment-prefix", "--comment-prefix-map", ".js=//",
            str(target)
        ]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_help_exits_0(self) -> None:
        """--help exits with code 0."""
        with patch("sys.argv", ["prog", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_multiple_files_all_match(self, tmp_path: Path) -> None:
        """Exit 0 when all files match."""
        snippet_file = tmp_path / "snippet.txt"
        snippet_file.write_text("hello")
        f1 = tmp_path / "f1.md"
        f1.write_text("hello")
        f2 = tmp_path / "f2.md"
        f2.write_text("hello world")

        with patch("sys.argv", [
            "prog", "--snippet-file", str(snippet_file), str(f1), str(f2)
        ]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_multiple_files_one_missing(self, tmp_path: Path) -> None:
        """Exit 1 when one file is missing the snippet."""
        snippet_file = tmp_path / "snippet.txt"
        snippet_file.write_text("hello")
        f1 = tmp_path / "f1.md"
        f1.write_text("hello")
        f2 = tmp_path / "f2.md"
        f2.write_text("goodbye")

        with patch("sys.argv", [
            "prog", "--snippet-file", str(snippet_file), str(f1), str(f2)
        ]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
