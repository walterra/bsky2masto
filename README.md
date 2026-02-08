# bsky2masto

Find followable Mastodon/Fediverse accounts from the people you follow on Bluesky, then generate a Mastodon import CSV.

## Features

- Fetches accounts followed by a Bluesky actor (`public.api.bsky.app`)
- Extracts possible Fediverse handles from bio/display name text
- Optional Bridgy-fed discovery (`@handle@bsky.brid.gy`)
- Optional WebFinger verification of discovered handles
- Exports CSV in Mastodon "Following list" import format

## Install

### Option A: install as a CLI

```bash
python3 -m pip install .
```

Then run:

```bash
bsky2masto --actor your-handle.bsky.social --include-bridgy
```

### Option B: developer mode

```bash
python3 -m pip install -e '.[dev]'
```

## Usage

```bash
bsky2masto \
  --actor your-handle.bsky.social \
  --output mastodon-import.csv \
  --matches-output matches.csv \
  --include-bridgy
```

You can also run directly from source (without console-script install):

```bash
python3 -m bsky2masto --actor your-handle.bsky.social --include-bridgy
```

### Useful flags

- `--verify` → verify extracted handles via WebFinger
- `--max-follows N` → scan only first `N` follows
- `--bridgy-pause-ms 150` → pause between Bridgy checks (default 150ms)
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
python3 -m pip install -e '.[dev]'
pytest
ruff check .
```

## Notes

- X/Twitter migration tools largely broke due to API restrictions.
- This tool is best-effort parsing. Review `matches.csv` before import.
