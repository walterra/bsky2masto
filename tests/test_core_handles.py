from bsky2masto.core import extract_candidates, normalize_handle


def test_normalize_handle_basic():
    assert normalize_handle("@Alice@Mastodon.Social") == "alice@mastodon.social"


def test_normalize_handle_rejects_invalid():
    assert normalize_handle("alice") is None
    assert normalize_handle("alice@localhost") is None
    assert normalize_handle("not valid@mastodon.social") is None


def test_extract_candidates_from_acct_pattern():
    text = "Find me at @alice@example.social and maybe @bob@social.example"
    candidates = extract_candidates(text)
    handles = {h for h, _ in candidates}
    assert "alice@example.social" in handles
    assert "bob@social.example" in handles


def test_extract_candidates_from_url_pattern():
    text = "Profiles: https://mastodon.social/@alice and https://hachyderm.io/users/bob"
    candidates = extract_candidates(text)
    handles = {h for h, _ in candidates}
    assert "alice@mastodon.social" in handles
    assert "bob@hachyderm.io" in handles
