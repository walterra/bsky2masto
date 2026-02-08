# bsky2masto

Find followable Mastodon/Fediverse accounts from the people you follow on Bluesky, then generate a Mastodon import CSV.

## Script

- `scripts/bsky2masto.py`

## What it does

1. Fetches accounts followed by a Bluesky actor (`public.api.bsky.app`)
2. Extracts possible Fediverse handles from profile text (bio/display name)
3. Optionally adds Bridgy-fed handles (`@handle@bsky.brid.gy`) for users who opted in
4. Writes a Mastodon import CSV (`Following list` format)

## Usage

```bash
python3 scripts/bsky2masto.py \
  --actor your-handle.bsky.social \
  --output mastodon-import.csv \
  --matches-output matches.csv \
  --include-bridgy
```

### Optional flags

- `--verify` → verify extracted handles via WebFinger (`https://domain/.well-known/webfinger`)
- `--max-follows N` → scan only first `N` follows (useful for testing)
- `--bridgy-pause-ms 150` → pause between Bridgy checks (default 150ms)

## Import into Mastodon

1. Open your Mastodon instance
2. Go to **Preferences → Import and export → Import**
3. Data type: **Following list**
4. Upload `mastodon-import.csv`

## Notes

- X/Twitter migration tools mostly stopped working due to API restrictions.
- This script is best-effort parsing. Keep `matches.csv` to review before import.
