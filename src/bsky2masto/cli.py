from __future__ import annotations

import argparse
import sys
from urllib.error import HTTPError, URLError

from .core import build_matches, log, write_mastodon_import_csv, write_matches_csv


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate a Mastodon import CSV from Bluesky follows",
    )
    p.add_argument("--actor", required=True, help="Bluesky handle or DID")
    p.add_argument(
        "--output",
        default="mastodon-import.csv",
        help="Output Mastodon import CSV path (default: mastodon-import.csv)",
    )
    p.add_argument(
        "--matches-output",
        default="matches.csv",
        help="Detailed match CSV path (default: matches.csv)",
    )
    p.add_argument(
        "--max-follows",
        type=int,
        default=None,
        help="Max follows to scan (for testing)",
    )
    p.add_argument(
        "--include-bridgy",
        action="store_true",
        help="Also include bridged Bluesky accounts as @handle@bsky.brid.gy",
    )
    p.add_argument(
        "--verify",
        action="store_true",
        help="Verify extracted Mastodon handles via WebFinger",
    )
    p.add_argument(
        "--bridgy-pause-ms",
        type=int,
        default=150,
        help="Pause between Bridgy checks to be polite (default: 150)",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress logging",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    verbose = not args.quiet

    try:
        matches, scanned = build_matches(
            actor=args.actor,
            max_follows=args.max_follows,
            include_bridgy=args.include_bridgy,
            verify=args.verify,
            bridgy_pause_ms=args.bridgy_pause_ms,
            verbose=verbose,
        )
    except HTTPError as e:
        print(f"HTTP error: {e.code} {e.reason}", file=sys.stderr)
        return 1
    except URLError as e:
        print(f"Network error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

    handles = [m.mastodon_handle for m in matches if m.verified != "no"]

    log("[3/3] Writing CSV files...", verbose)
    write_mastodon_import_csv(args.output, handles)
    write_matches_csv(args.matches_output, matches)

    unique_handles = len(set(handles))
    print(f"Scanned follows: {scanned}")
    print(f"Matches found: {len(matches)}")
    print(f"Unique importable handles: {unique_handles}")
    print(f"Wrote Mastodon import CSV: {args.output}")
    print(f"Wrote detailed matches CSV: {args.matches_output}")

    return 0
