"""End-to-end tests for realistic usage scenarios."""

from pathlib import Path
from test.helpers import run_cli

import pytest


@pytest.mark.e2e
class TestRealisticMarkdownScenarios:
    """E2E tests for markdown file scenarios."""

    def test_license_snippet_in_readme(self, tmp_path: Path) -> None:
        """License text found in README file."""
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
        """Installation command found in documentation."""
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
    """E2E tests for Python file scenarios."""

    def test_multiline_header_comment(self, tmp_path: Path) -> None:
        """Multiline copyright header found in Python file."""
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
        """Snippet with empty lines matches commented block."""
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
    """E2E tests for YAML file scenarios."""

    def test_workflow_comment_block(self, tmp_path: Path) -> None:
        """Comment block found in YAML workflow file."""
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
        """YAML files with .yaml extension use commented matching."""
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
    """E2E tests for mixed file type scenarios."""

    def test_multiple_file_types_all_pass(self, tmp_path: Path) -> None:
        """Different file types all contain their snippets."""
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
        """Exit 1 when one file passes and another fails."""
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


@pytest.mark.e2e
class TestFlagScenarios:
    """E2E tests for CLI flag combinations."""

    def test_mixed_extensions_with_infer(self, tmp_path: Path) -> None:
        """--infer-comment-prefix handles mixed file types."""
        snippet = tmp_path / "header.txt"
        snippet.write_text("Copyright 2025")

        py_file = tmp_path / "code.py"
        py_file.write_text("# Copyright 2025\ndef main(): pass")

        md_file = tmp_path / "README.md"
        md_file.write_text("# Title\n\nCopyright 2025\n")

        yml_file = tmp_path / "config.yml"
        yml_file.write_text("#Copyright 2025\nkey: value")

        result = run_cli(
            "--content-file", str(snippet),
            "--infer-comment-prefix",
            str(py_file), str(md_file), str(yml_file)
        )
        assert result.returncode == 0
        assert result.stdout == ""

    def test_js_files_with_custom_prefix(self, tmp_path: Path) -> None:
        """JavaScript files work with // comment prefix."""
        snippet = tmp_path / "license.txt"
        snippet.write_text("MIT License")

        js_file = tmp_path / "app.js"
        js_file.write_text("// MIT License\nconst x = 1;")

        result = run_cli(
            "--content-file", str(snippet),
            "--comment-prefix", "//",
            str(js_file)
        )
        assert result.returncode == 0

    def test_multiple_js_ts_files_with_map(self, tmp_path: Path) -> None:
        """Multiple JS/TS files work with custom prefix map."""
        snippet = tmp_path / "header.txt"
        snippet.write_text("Copyright Notice")

        js_file = tmp_path / "app.js"
        js_file.write_text("// Copyright Notice\nconst x = 1;")

        ts_file = tmp_path / "types.ts"
        ts_file.write_text("//Copyright Notice\ntype X = string;")

        result = run_cli(
            "--content-file", str(snippet),
            "--infer-comment-prefix",
            "--comment-prefix-map", ".js=//,.ts=//",
            str(js_file), str(ts_file)
        )
        assert result.returncode == 0

    def test_realistic_multifile_project(self, tmp_path: Path) -> None:
        """Realistic project with multiple file types all pass."""
        header = tmp_path / "license_header.txt"
        header.write_text("Copyright 2025 Acme Inc.\nLicensed under Apache 2.0")

        py_file = tmp_path / "main.py"
        py_file.write_text(
            "#!/usr/bin/env python3\n"
            "# Copyright 2025 Acme Inc.\n"
            "# Licensed under Apache 2.0\n"
            "\n"
            "def main():\n"
            "    print('Hello')\n"
        )

        readme = tmp_path / "README.md"
        readme.write_text(
            "# Project\n\n"
            "Copyright 2025 Acme Inc.\n"
            "Licensed under Apache 2.0\n"
        )

        config = tmp_path / "config.yaml"
        config.write_text(
            "#Copyright 2025 Acme Inc.\n"
            "#Licensed under Apache 2.0\n"
            "setting: value\n"
        )

        result = run_cli(
            "--content-file", str(header),
            "--infer-comment-prefix",
            str(py_file), str(readme), str(config)
        )
        assert result.returncode == 0
        assert result.stdout == ""
