from pathlib import Path


def raw_match(snippet: str, file_content: str) -> bool:
    return snippet in file_content


def commented_match(snippet: str, file_content: str) -> bool:
    snippet_lines = snippet.splitlines()
    if not snippet_lines:
        return True

    file_lines = file_content.splitlines()
    if not file_lines:
        return False

    def line_matches(snippet_line: str, file_line: str) -> bool:
        if snippet_line == "":
            return file_line == "" or file_line.rstrip() == "#"
        return file_line in (f"# {snippet_line}", f"#{snippet_line}")

    for start_idx, file_line in enumerate(file_lines):
        if line_matches(snippet_lines[0], file_line):
            if start_idx + len(snippet_lines) > len(file_lines):
                continue
            all_match = True
            for offset, snippet_line in enumerate(snippet_lines):
                if not line_matches(snippet_line, file_lines[start_idx + offset]):
                    all_match = False
                    break
            if all_match:
                return True
    return False


def check_file(snippet: str, file_path: Path) -> bool:
    file_content = file_path.read_text()
    suffix = file_path.suffix.lower()

    if suffix == ".md":
        return raw_match(snippet, file_content)
    if suffix in (".py", ".yml", ".yaml"):
        return commented_match(snippet, file_content)

    return raw_match(snippet, file_content)
