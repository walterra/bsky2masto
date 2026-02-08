# bsky2masto

Find followable Mastodon/Fediverse accounts from the people you follow on Bluesky, then generate a Mastodon import CSV.

## Features

- Fetches accounts followed by a Bluesky actor (`public.api.bsky.app`)
- Extracts possible Fediverse handles from bio/display name text
- Optional Bridgy-fed discovery (`@handle@bsky.brid.gy`)
- Optional WebFinger verification of discovered handles
- Exports CSV in Mastodon "Following list" import format

## Install (uv-first)

```bash
uv sync --group dev
```

Run the CLI with uv:

```bash
uv run bsky2masto --actor your-handle.bsky.social --include-bridgy
```

Optional (non-uv) install:

```bash
python3 -m pip install .
```

`uv.lock` is committed for reproducible environments.

## Usage

```bash
uv run bsky2masto \
  --actor your-handle.bsky.social \
  --output mastodon-import.csv \
  --matches-output matches.csv \
  --include-bridgy
```

You can also run directly from source:

```bash
uv run python -m bsky2masto --actor your-handle.bsky.social --include-bridgy
```

### Useful flags

- `--verify` → verify extracted handles via WebFinger
- `--max-follows N` → scan only first `N` follows
- `--scan-workers 8` → parallel workers for verify/bridgy checks (queue-based)
- `--bridgy-pause-ms 150` → per-check pause before Bridgy request (politeness throttle)
- `--quiet` → suppress progress logging

## Import into Mastodon

1. Open your Mastodon instance
2. Go to **Preferences → Import and export → Import**
3. Data type: **Following list**
4. Upload `mastodon-import.csv`

## Project layout

- `src/bsky2masto/` → installable package
- `tests/` → pytest suite

## Development

```bash
uv sync --group dev
uv run pytest
uv run ruff check .
```

## Notes

- X/Twitter migration tools largely broke due to API restrictions.
- This tool is best-effort parsing. Review `matches.csv` before import.
