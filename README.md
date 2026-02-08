# bsky2masto

Find followable Mastodon/Fediverse accounts from the people you follow on Bluesky, then generate a Mastodon import CSV.

## What it does

Given a Bluesky account, `bsky2masto`:

1. Fetches followed accounts via the public Bluesky API
2. Extracts possible Fediverse handles from bios/display names
3. Optionally checks Bridgy Fed opt-in (`@handle@bsky.brid.gy`)
4. Optionally verifies discovered handles with WebFinger
5. Writes:
   - `mastodon-import.csv` (Mastodon "Following list" import format)
   - `matches.csv` (detailed match diagnostics)

## Installation

### Recommended (end users): pipx

```bash
pipx install bsky2masto
```

> If the first PyPI release is not live yet, use the "From source" section below.

### One-shot usage: uvx

```bash
uvx bsky2masto --actor your-handle.bsky.social --include-bridgy
```

### Standard pip

```bash
python -m pip install bsky2masto
```

### From source (development)

```bash
uv sync --group dev
uv run bsky2masto --actor your-handle.bsky.social --include-bridgy
```

## Quickstart

```bash
bsky2masto \
  --actor your-handle.bsky.social \
  --output mastodon-import.csv \
  --matches-output matches.csv \
  --include-bridgy
```

Useful flags:

- `--verify` → verify discovered handles via WebFinger
- `--max-follows N` → scan only first `N` follows (faster testing)
- `--scan-workers N` → worker count for verify/bridgy checks (default: `8`)
- `--bridgy-pause-ms N` → per-check Bridgy pause (default: `150`)
- `--quiet` → suppress progress logs
- `--version` → print CLI version

## Import into Mastodon

1. Open your Mastodon instance
2. Go to **Preferences → Import and export → Import**
3. Data type: **Following list**
4. Upload `mastodon-import.csv`

## Exit codes

- `0` success
- `1` network/HTTP/unexpected runtime error
- `2` CLI usage error (argparse)

## Limitations and expectations

- Best-effort parsing: false positives are possible.
- Always inspect `matches.csv` before importing.
- `--verify` and Bridgy checks perform additional network requests and may be slower.
- Some profile strings (emails, non-Mastodon `@` patterns) can still look handle-like.

## Development

```bash
uv sync --group dev
uv run ruff check .
uv run pytest -q
uv build
```

Supported Python versions: 3.10+

## Security

For vulnerability reports, see [SECURITY.md](SECURITY.md).
