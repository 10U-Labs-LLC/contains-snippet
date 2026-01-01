import argparse
import sys
from pathlib import Path

from .matcher import check_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check if a snippet exists in files"
    )
    parser.add_argument(
        "--content-file",
        required=True,
        type=Path,
        help="Path to the file containing the snippet to search for",
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="Files to check for the snippet",
    )

    try:
        args = parser.parse_args()
    except SystemExit as e:
        sys.exit(2 if e.code != 0 else 0)

    try:
        snippet = args.content_file.read_text()
    except (OSError, IOError) as e:
        print(f"Error reading content file: {e}", file=sys.stderr)
        sys.exit(2)

    results = []
    for file_path in args.files:
        try:
            result = check_file(snippet, file_path)
            results.append(result)
        except (OSError, IOError) as e:
            print(f"Error reading file {file_path}: {e}", file=sys.stderr)
            sys.exit(2)

    sys.exit(0 if all(results) else 1)
