from pathlib import Path

import pytest

from contains_snippet.cli import parse_prefix_map
from contains_snippet.matcher import check_file, commented_match, raw_match


@pytest.mark.unit
class TestRawMatch:
    def test_exact_match(self) -> None:
        assert raw_match("hello", "hello")

    def test_substring_match(self) -> None:
        assert raw_match("world", "hello world!")

    def test_multiline_match(self) -> None:
        snippet = "line1\nline2"
        content = "prefix\nline1\nline2\nsuffix"
        assert raw_match(snippet, content)

    def test_no_match(self) -> None:
        assert not raw_match("xyz", "abc")

    def test_empty_snippet(self) -> None:
        assert raw_match("", "any content")

    def test_empty_content(self) -> None:
        assert not raw_match("something", "")


@pytest.mark.unit
class TestCommentedMatch:
    def test_single_line_with_space(self) -> None:
        assert commented_match("hello", "# hello")

    def test_single_line_without_space(self) -> None:
        assert commented_match("hello", "#hello")

    def test_multiline_with_space(self) -> None:
        snippet = "line1\nline2"
        content = "# line1\n# line2"
        assert commented_match(snippet, content)

    def test_multiline_without_space(self) -> None:
        snippet = "line1\nline2"
        content = "#line1\n#line2"
        assert commented_match(snippet, content)

    def test_multiline_mixed_space(self) -> None:
        snippet = "line1\nline2"
        content = "# line1\n#line2"
        assert commented_match(snippet, content)

    def test_empty_line_matches_empty(self) -> None:
        snippet = "before\n\nafter"
        content = "# before\n\n# after"
        assert commented_match(snippet, content)

    def test_empty_line_matches_hash(self) -> None:
        snippet = "before\n\nafter"
        content = "# before\n#\n# after"
        assert commented_match(snippet, content)

    def test_empty_line_matches_hash_with_spaces(self) -> None:
        snippet = "before\n\nafter"
        content = "# before\n#   \n# after"
        assert commented_match(snippet, content)

    def test_snippet_in_middle_of_file(self) -> None:
        snippet = "target"
        content = "# other\n# target\n# more"
        assert commented_match(snippet, content)

    def test_no_match(self) -> None:
        assert not commented_match("hello", "# goodbye")

    def test_partial_match_not_contiguous(self) -> None:
        snippet = "line1\nline2"
        content = "# line1\n# other\n# line2"
        assert not commented_match(snippet, content)

    def test_empty_snippet(self) -> None:
        assert commented_match("", "# anything")

    def test_empty_content(self) -> None:
        assert not commented_match("hello", "")


@pytest.mark.unit
class TestCheckFile:
    def test_md_file_raw_match(self, tmp_path: Path) -> None:
        md_file = tmp_path / "test.md"
        md_file.write_text("some content here")
        assert check_file("content", md_file)

    def test_md_file_no_match(self, tmp_path: Path) -> None:
        md_file = tmp_path / "test.md"
        md_file.write_text("some content here")
        assert not check_file("missing", md_file)

    def test_py_file_commented_match(self, tmp_path: Path) -> None:
        py_file = tmp_path / "test.py"
        py_file.write_text("# snippet line")
        assert check_file("snippet line", py_file)

    def test_py_file_no_match(self, tmp_path: Path) -> None:
        py_file = tmp_path / "test.py"
        py_file.write_text("snippet line")
        assert not check_file("snippet line", py_file)

    def test_yml_file_commented_match(self, tmp_path: Path) -> None:
        yml_file = tmp_path / "test.yml"
        yml_file.write_text("# config line")
        assert check_file("config line", yml_file)

    def test_yaml_file_commented_match(self, tmp_path: Path) -> None:
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("#config line")
        assert check_file("config line", yaml_file)

    def test_unknown_extension_raw_match(self, tmp_path: Path) -> None:
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("plain text content")
        assert check_file("text", txt_file)


@pytest.mark.unit
class TestCommentedMatchWithPrefix:
    def test_custom_prefix_double_slash(self) -> None:
        assert commented_match("hello", "// hello", prefix="//")

    def test_custom_prefix_semicolon(self) -> None:
        assert commented_match("hello", "; hello", prefix=";")

    def test_custom_prefix_no_space(self) -> None:
        assert commented_match("hello", "//hello", prefix="//")

    def test_custom_prefix_multiline(self) -> None:
        snippet = "line1\nline2"
        content = "// line1\n// line2"
        assert commented_match(snippet, content, prefix="//")

    def test_custom_prefix_empty_line(self) -> None:
        snippet = "before\n\nafter"
        content = "// before\n//\n// after"
        assert commented_match(snippet, content, prefix="//")


@pytest.mark.unit
class TestParsePrefixMap:
    def test_single_entry(self) -> None:
        assert parse_prefix_map(".py=#") == {".py": "#"}

    def test_multiple_entries(self) -> None:
        result = parse_prefix_map(".py=#,.js=//,.md=raw")
        assert result == {".py": "#", ".js": "//", ".md": None}

    def test_raw_value(self) -> None:
        assert parse_prefix_map(".txt=raw") == {".txt": None}

    def test_raw_case_insensitive(self) -> None:
        assert parse_prefix_map(".txt=RAW") == {".txt": None}

    def test_extension_normalized_lowercase(self) -> None:
        assert parse_prefix_map(".PY=#") == {".py": "#"}

    def test_whitespace_stripped(self) -> None:
        assert parse_prefix_map(" .py = # ") == {".py": "#"}


@pytest.mark.unit
class TestCheckFileWithCommentPrefix:
    def test_forces_commented_on_md(self, tmp_path: Path) -> None:
        md_file = tmp_path / "test.md"
        md_file.write_text("# hello")
        assert check_file("hello", md_file, comment_prefix="#")

    def test_custom_prefix_on_any_file(self, tmp_path: Path) -> None:
        js_file = tmp_path / "test.js"
        js_file.write_text("// hello")
        assert check_file("hello", js_file, comment_prefix="//")


@pytest.mark.unit
class TestCheckFileWithPrefixMap:
    def test_prefix_map_uses_mapped_prefix(self, tmp_path: Path) -> None:
        md_file = tmp_path / "test.md"
        md_file.write_text("# hello")
        prefix_map: dict[str, str | None] = {".md": "#"}
        assert check_file("hello", md_file, prefix_map=prefix_map)

    def test_prefix_map_raw_value(self, tmp_path: Path) -> None:
        py_file = tmp_path / "test.py"
        py_file.write_text("hello")
        prefix_map: dict[str, str | None] = {".py": None}
        assert check_file("hello", py_file, prefix_map=prefix_map)

    def test_prefix_map_unknown_ext_defaults_raw(self, tmp_path: Path) -> None:
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("hello")
        prefix_map: dict[str, str | None] = {".py": "#"}
        assert check_file("hello", txt_file, prefix_map=prefix_map)

    def test_prefix_map_unknown_ext_uses_raw(self, tmp_path: Path) -> None:
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("# hello\n# world")
        prefix_map: dict[str, str | None] = {".py": "#"}
        assert not check_file("hello\nworld", txt_file, prefix_map=prefix_map)
