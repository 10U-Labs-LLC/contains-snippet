# contains-snippet

A command-line tool that checks whether a given snippet exists anywhere within a file. For plain text files (like `.md`), it searches the raw content directly. For source code files (`.py`, `.yml`, `.yaml`), it checks for the snippet rendered as comments.

## Installation

```bash
pip install -e .
```

## Usage

```bash
contains-snippet --content-file SNIPPET_FILE FILE [FILE ...]
```

### Exit Codes

- `0` - All files contain the snippet
- `1` - One or more files are missing the snippet
- `2` - Usage/configuration/runtime error

### Matching Rules

- `.md` files: Raw substring match
- `.py`, `.yml`, `.yaml` files: Commented match (lines prefixed with `# ` or `#`)

### Examples

Check if a license notice appears in a README:

```bash
contains-snippet --content-file license_notice.txt README.md
```

Check if a header comment exists in multiple Python files:

```bash
contains-snippet --content-file header.txt src/*.py
```

## CI Checks

The following checks run on every push and pull request:

- **yamllint** - YAML linting for workflow files
- **pylint** - Python linting for source and test code
- **mypy** - Static type checking for source code
- **jscpd** - Duplicate code detection
- **pytest** - Unit, integration, and E2E tests
