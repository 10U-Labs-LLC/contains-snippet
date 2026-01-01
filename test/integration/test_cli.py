import subprocess
import sys
from pathlib import Path

import pytest


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "contains_snippet", *args],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.integration
class TestCliExitCodes:
    def test_exit_0_when_snippet_found(self, tmp_path: Path) -> None:
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("hello")
        target_file = tmp_path / "target.md"
        target_file.write_text("say hello world")

        result = run_cli("--content-file", str(content_file), str(target_file))
        assert result.returncode == 0
        assert result.stdout == ""

    def test_exit_1_when_snippet_missing(self, tmp_path: Path) -> None:
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("missing")
        target_file = tmp_path / "target.md"
        target_file.write_text("no match here")

        result = run_cli("--content-file", str(content_file), str(target_file))
        assert result.returncode == 1
        assert result.stdout == ""

    def test_exit_2_missing_content_file_arg(self) -> None:
        result = run_cli("somefile.md")
        assert result.returncode == 2

    def test_exit_2_missing_target_files(self, tmp_path: Path) -> None:
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("hello")

        result = run_cli("--content-file", str(content_file))
        assert result.returncode == 2

    def test_exit_2_unreadable_content_file(self, tmp_path: Path) -> None:
        target_file = tmp_path / "target.md"
        target_file.write_text("content")

        result = run_cli(
            "--content-file", "/nonexistent/path/file.txt", str(target_file)
        )
        assert result.returncode == 2

    def test_exit_2_unreadable_target_file(self, tmp_path: Path) -> None:
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("hello")

        result = run_cli(
            "--content-file", str(content_file), "/nonexistent/path/file.md"
        )
        assert result.returncode == 2


@pytest.mark.integration
class TestCliMultipleFiles:
    def test_all_files_match(self, tmp_path: Path) -> None:
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("target")
        file1 = tmp_path / "file1.md"
        file1.write_text("has target text")
        file2 = tmp_path / "file2.md"
        file2.write_text("also has target")

        result = run_cli("--content-file", str(content_file), str(file1), str(file2))
        assert result.returncode == 0
        assert result.stdout == ""

    def test_one_file_missing(self, tmp_path: Path) -> None:
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("target")
        file1 = tmp_path / "file1.md"
        file1.write_text("has target text")
        file2 = tmp_path / "file2.md"
        file2.write_text("no match")

        result = run_cli("--content-file", str(content_file), str(file1), str(file2))
        assert result.returncode == 1
        assert result.stdout == ""


@pytest.mark.integration
class TestCliCommentedMatch:
    def test_py_file_commented(self, tmp_path: Path) -> None:
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("snippet content")
        py_file = tmp_path / "code.py"
        py_file.write_text("# snippet content\ncode = 1")

        result = run_cli("--content-file", str(content_file), str(py_file))
        assert result.returncode == 0
        assert result.stdout == ""

    def test_yml_file_commented(self, tmp_path: Path) -> None:
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("config line")
        yml_file = tmp_path / "config.yml"
        yml_file.write_text("#config line\nkey: value")

        result = run_cli("--content-file", str(content_file), str(yml_file))
        assert result.returncode == 0
        assert result.stdout == ""
