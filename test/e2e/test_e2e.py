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


@pytest.mark.e2e
class TestRealisticMarkdownScenarios:
    def test_license_snippet_in_readme(self, tmp_path: Path) -> None:
        snippet = tmp_path / "license_notice.txt"
        snippet.write_text("Licensed under the Apache License, Version 2.0")

        readme = tmp_path / "README.md"
        readme.write_text(
            "# My Project\n\n"
            "Some description here.\n\n"
            "## License\n\n"
            "Licensed under the Apache License, Version 2.0\n"
        )

        result = run_cli("--content-file", str(snippet), str(readme))
        assert result.returncode == 0

    def test_code_block_in_docs(self, tmp_path: Path) -> None:
        snippet = tmp_path / "example.txt"
        snippet.write_text("pip install my-package")

        docs = tmp_path / "INSTALL.md"
        docs.write_text(
            "# Installation\n\n"
            "Run the following:\n\n"
            "```bash\n"
            "pip install my-package\n"
            "```\n"
        )

        result = run_cli("--content-file", str(snippet), str(docs))
        assert result.returncode == 0


@pytest.mark.e2e
class TestRealisticPythonScenarios:
    def test_multiline_header_comment(self, tmp_path: Path) -> None:
        snippet = tmp_path / "header.txt"
        snippet.write_text("Copyright 2025\nAll rights reserved")

        py_file = tmp_path / "module.py"
        py_file.write_text(
            "#!/usr/bin/env python\n"
            "# Copyright 2025\n"
            "# All rights reserved\n"
            "\n"
            "def main():\n"
            "    pass\n"
        )

        result = run_cli("--content-file", str(snippet), str(py_file))
        assert result.returncode == 0

    def test_snippet_with_empty_lines(self, tmp_path: Path) -> None:
        snippet = tmp_path / "docblock.txt"
        snippet.write_text("Section 1\n\nSection 2")

        py_file = tmp_path / "code.py"
        py_file.write_text(
            "# Section 1\n"
            "#\n"
            "# Section 2\n"
            "x = 1\n"
        )

        result = run_cli("--content-file", str(snippet), str(py_file))
        assert result.returncode == 0


@pytest.mark.e2e
class TestRealisticYamlScenarios:
    def test_workflow_comment_block(self, tmp_path: Path) -> None:
        snippet = tmp_path / "notice.txt"
        snippet.write_text("Auto-generated file\nDo not edit manually")

        workflow = tmp_path / "ci.yml"
        workflow.write_text(
            "# Auto-generated file\n"
            "# Do not edit manually\n"
            "\n"
            "name: CI\n"
            "on: push\n"
        )

        result = run_cli("--content-file", str(snippet), str(workflow))
        assert result.returncode == 0

    def test_yaml_extension(self, tmp_path: Path) -> None:
        snippet = tmp_path / "config_header.txt"
        snippet.write_text("Configuration file")

        config = tmp_path / "settings.yaml"
        config.write_text(
            "#Configuration file\n"
            "database:\n"
            "  host: localhost\n"
        )

        result = run_cli("--content-file", str(snippet), str(config))
        assert result.returncode == 0


@pytest.mark.e2e
class TestMixedFileTypes:
    def test_multiple_file_types_all_pass(self, tmp_path: Path) -> None:
        md_snippet = tmp_path / "md_snippet.txt"
        md_snippet.write_text("Important Notice")

        readme = tmp_path / "README.md"
        readme.write_text("# Title\n\nImportant Notice\n")

        result = run_cli("--content-file", str(md_snippet), str(readme))
        assert result.returncode == 0

        py_snippet = tmp_path / "py_snippet.txt"
        py_snippet.write_text("TODO: implement")

        code = tmp_path / "main.py"
        code.write_text("# TODO: implement\ndef func(): pass\n")

        yml_snippet = tmp_path / "yml_snippet.txt"
        yml_snippet.write_text("version 1.0")

        config = tmp_path / "config.yml"
        config.write_text("#version 1.0\nkey: value\n")

        result = run_cli(
            "--content-file",
            str(md_snippet),
            str(readme),
        )
        assert result.returncode == 0

    def test_mixed_pass_fail(self, tmp_path: Path) -> None:
        snippet = tmp_path / "required.txt"
        snippet.write_text("REQUIRED TEXT")

        file1 = tmp_path / "has_it.md"
        file1.write_text("This has REQUIRED TEXT in it")

        file2 = tmp_path / "missing.md"
        file2.write_text("This does not have the text")

        result = run_cli(
            "--content-file", str(snippet), str(file1), str(file2)
        )
        assert result.returncode == 1
        assert result.stdout == ""
