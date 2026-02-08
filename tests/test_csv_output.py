import csv

from bsky2masto.core import Match, write_mastodon_import_csv, write_matches_csv


def test_write_mastodon_import_csv_dedupes_and_sorts(tmp_path):
    out = tmp_path / "import.csv"
    write_mastodon_import_csv(
        str(out),
        ["bob@example.com", "alice@example.com", "bob@example.com"],
    )

    rows = list(csv.reader(out.read_text(encoding="utf-8").splitlines()))
    assert rows[0] == ["Account address", "Show boosts", "Notify on new posts", "Languages"]
    assert rows[1][0] == "alice@example.com"
    assert rows[2][0] == "bob@example.com"
    assert len(rows) == 3


def test_write_matches_csv_headers_and_content(tmp_path):
    out = tmp_path / "matches.csv"
    write_matches_csv(
        str(out),
        [
            Match(
                bluesky_handle="alice.bsky.social",
                bluesky_display_name="Alice",
                mastodon_handle="alice@example.com",
                source="acct_in_profile",
                verified="yes",
            )
        ],
    )

    rows = list(csv.reader(out.read_text(encoding="utf-8").splitlines()))
    assert rows[0] == [
        "Bluesky handle",
        "Bluesky display name",
        "Mastodon handle",
        "Source",
        "Verified",
    ]
    assert rows[1] == [
        "alice.bsky.social",
        "Alice",
        "alice@example.com",
        "acct_in_profile",
        "yes",
    ]
