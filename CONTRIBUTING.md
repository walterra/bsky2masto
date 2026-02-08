# Contributing

Thanks for your interest in improving `bsky2masto`.

## Development setup

```bash
uv sync --group dev
```

Run checks before opening a PR:

```bash
uv run ruff check .
uv run pytest -q
uv build
```

## Coding guidelines

- Keep CLI behavior explicit and user-friendly.
- Preserve compatibility with Python 3.10+.
- Add tests for new parsing behavior and CSV output changes.
- Keep README examples copy/paste ready.

## Pull requests

Please include:

- What changed
- Why it changed
- How you validated it (tests, example command, output)

If behavior changes for end users, update `README.md` in the same PR.

## Reporting bugs

Use the bug report issue template and include:

- command used
- Python version
- OS
- sanitized sample input/output
