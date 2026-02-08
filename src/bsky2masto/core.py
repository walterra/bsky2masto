from __future__ import annotations

import csv
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BSKY_API_BASE = "https://public.api.bsky.app/xrpc"
DEFAULT_TIMEOUT = 12

# @user@domain (with optional leading @)
ACCT_RE = re.compile(
    r"(?<![\w/])@?([A-Za-z0-9_][A-Za-z0-9._-]{0,63})@([A-Za-z0-9.-]+\.[A-Za-z]{2,})(?![\w.-])"
)

# https://domain/@user  or  https://domain/users/user  or  https://domain/u/user
URL_HANDLE_RE = re.compile(
    r"https?://([A-Za-z0-9.-]+\.[A-Za-z]{2,})/(?:@|users/|u/)([A-Za-z0-9_][A-Za-z0-9._-]{0,63})",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Match:
    bluesky_handle: str
    bluesky_display_name: str
    mastodon_handle: str
    source: str
    verified: str  # yes / no / skipped


def log(message: str, enabled: bool = True) -> None:
    if enabled:
        print(message, flush=True)


def http_json(url: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    req = Request(
        url,
        headers={
            "User-Agent": "bsky2masto/0.1.0",
            "Accept": "application/json, application/jrd+json;q=0.9, */*;q=0.1",
        },
    )
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def bsky_get(endpoint: str, params: Dict[str, str]) -> dict:
    query = urlencode(params)
    url = f"{BSKY_API_BASE}/{endpoint}?{query}"
    return http_json(url)


def fetch_follows(
    actor: str, max_follows: Optional[int] = None, verbose: bool = True
) -> List[dict]:
    follows: List[dict] = []
    cursor: Optional[str] = None
    page = 0

    log(f"[1/3] Fetching follows for {actor}...", verbose)

    while True:
        params = {"actor": actor, "limit": "100"}
        if cursor:
            params["cursor"] = cursor

        payload = bsky_get("app.bsky.graph.getFollows", params)
        batch = payload.get("follows", [])
        follows.extend(batch)
        page += 1
        log(f"  page {page}: +{len(batch)} (total {len(follows)})", verbose)

        if max_follows is not None and len(follows) >= max_follows:
            follows = follows[:max_follows]
            break

        cursor = payload.get("cursor")
        if not cursor:
            break

    log(f"Fetched {len(follows)} follows", verbose)
    return follows


def normalize_handle(raw: str) -> Optional[str]:
    h = raw.strip().strip('"\'()[]{}<>,.;:!?')
    if h.startswith("@"):
        h = h[1:]

    if h.count("@") != 1:
        return None

    local, domain = h.split("@", 1)
    local = local.strip()
    domain = domain.strip().strip(".").lower()

    if not local or not domain:
        return None
    if "." not in domain:
        return None
    if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9._-]{0,100}", local):
        return None
    if not re.fullmatch(r"[A-Za-z0-9.-]+", domain):
        return None

    return f"{local.lower()}@{domain}"


def extract_candidates(text: str) -> List[Tuple[str, str]]:
    if not text:
        return []

    out: List[Tuple[str, str]] = []

    for local, domain in ACCT_RE.findall(text):
        h = normalize_handle(f"{local}@{domain}")
        if h:
            out.append((h, "acct_in_profile"))

    for domain, local in URL_HANDLE_RE.findall(text):
        h = normalize_handle(f"{local}@{domain}")
        if h:
            out.append((h, "url_in_profile"))

    return out


def is_bridged_to_fediverse(bsky_handle: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
    resource = urlencode({"resource": f"acct:{bsky_handle}@bsky.brid.gy"})
    url = f"https://bsky.brid.gy/.well-known/webfinger?{resource}"
    try:
        _ = http_json(url, timeout=timeout)
        return True
    except Exception:
        return False


def verify_mastodon_handle(handle: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
    local, domain = handle.split("@", 1)
    resource = urlencode({"resource": f"acct:{local}@{domain}"})
    url = f"https://{domain}/.well-known/webfinger?{resource}"
    try:
        _ = http_json(url, timeout=timeout)
        return True
    except Exception:
        return False


def write_mastodon_import_csv(path: str, handles: Iterable[str]) -> None:
    rows = sorted(set(handles))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Account address", "Show boosts", "Notify on new posts", "Languages"])
        for h in rows:
            w.writerow([h, "true", "false", ""])


def write_matches_csv(path: str, matches: Iterable[Match]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "Bluesky handle",
                "Bluesky display name",
                "Mastodon handle",
                "Source",
                "Verified",
            ]
        )
        for m in sorted(matches, key=lambda x: (x.mastodon_handle, x.bluesky_handle)):
            w.writerow(
                [
                    m.bluesky_handle,
                    m.bluesky_display_name,
                    m.mastodon_handle,
                    m.source,
                    m.verified,
                ]
            )


def _verify_candidates_parallel(
    candidates: Set[str], workers: int, verbose: bool
) -> Dict[str, bool]:
    if not candidates:
        return {}

    worker_count = max(1, workers)
    log(
        f"  verifying {len(candidates)} unique discovered handles with {worker_count} workers...",
        verbose,
    )

    results: Dict[str, bool] = {}
    sorted_candidates = sorted(candidates)

    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        future_to_candidate = {
            pool.submit(verify_mastodon_handle, candidate): candidate
            for candidate in sorted_candidates
        }

        total = len(future_to_candidate)
        done = 0
        for future in as_completed(future_to_candidate):
            candidate = future_to_candidate[future]
            try:
                results[candidate] = bool(future.result())
            except Exception:
                results[candidate] = False

            done += 1
            if verbose and (done % 25 == 0 or done == total):
                log(f"    verified {done}/{total}", verbose)

    return results


def _bridgy_lookup_worker(handle: str, pause_ms: int) -> bool:
    if pause_ms > 0:
        time.sleep(pause_ms / 1000.0)
    return is_bridged_to_fediverse(handle)


def _check_bridgy_parallel(
    handles: List[str], workers: int, pause_ms: int, verbose: bool
) -> Set[str]:
    filtered_handles = [h for h in handles if h]
    if not filtered_handles:
        return set()

    worker_count = max(1, workers)
    log(
        f"  checking Bridgy Fed opt-in for {len(filtered_handles)} follows "
        f"with {worker_count} workers...",
        verbose,
    )

    bridged: Set[str] = set()
    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        future_to_handle = {
            pool.submit(_bridgy_lookup_worker, handle, pause_ms): handle
            for handle in filtered_handles
        }

        total = len(future_to_handle)
        done = 0
        for future in as_completed(future_to_handle):
            handle = future_to_handle[future]
            try:
                if bool(future.result()):
                    bridged.add(handle)
            except Exception:
                pass

            done += 1
            if verbose and (done % 50 == 0 or done == total):
                log(f"    bridgy checked {done}/{total}", verbose)

    return bridged


def build_matches(
    actor: str,
    max_follows: Optional[int],
    include_bridgy: bool,
    verify: bool,
    bridgy_pause_ms: int,
    scan_workers: int,
    verbose: bool,
) -> Tuple[List[Match], int]:
    follows = fetch_follows(actor=actor, max_follows=max_follows, verbose=verbose)
    profile_rows: List[Tuple[str, str, List[Tuple[str, str]]]] = []
    all_candidates: Set[str] = set()
    all_handles: List[str] = []

    log(
        f"[2/3] Scanning {len(follows)} followed profiles "
        f"(verify={'on' if verify else 'off'}, bridgy={'on' if include_bridgy else 'off'}, "
        f"workers={max(1, scan_workers)})...",
        verbose,
    )

    for idx, f in enumerate(follows, start=1):
        bsky_handle = (f.get("handle") or "").strip()
        display_name = (f.get("displayName") or "").strip()
        description = f.get("description") or ""

        log(f"  [{idx}/{len(follows)}] {bsky_handle}", verbose)

        seen_for_profile: Set[str] = set()
        profile_candidates: List[Tuple[str, str]] = []

        for candidate, source in extract_candidates(description) + extract_candidates(display_name):
            if candidate in seen_for_profile:
                continue
            seen_for_profile.add(candidate)
            profile_candidates.append((candidate, source))

        if verify:
            for candidate, _ in profile_candidates:
                all_candidates.add(candidate)

        if include_bridgy and bsky_handle:
            all_handles.append(bsky_handle)

        profile_rows.append((bsky_handle, display_name, profile_candidates))

    verify_results = (
        _verify_candidates_parallel(all_candidates, scan_workers, verbose) if verify else {}
    )
    bridged_handles = (
        _check_bridgy_parallel(all_handles, scan_workers, bridgy_pause_ms, verbose)
        if include_bridgy
        else set()
    )

    matches: List[Match] = []
    for bsky_handle, display_name, profile_candidates in profile_rows:
        for candidate, source in profile_candidates:
            if verify:
                verified = "yes" if verify_results.get(candidate, False) else "no"
            else:
                verified = "skipped"

            matches.append(
                Match(
                    bluesky_handle=bsky_handle,
                    bluesky_display_name=display_name,
                    mastodon_handle=candidate,
                    source=source,
                    verified=verified,
                )
            )

        if include_bridgy and bsky_handle in bridged_handles:
            bridgy_handle = f"{bsky_handle}@bsky.brid.gy"
            matches.append(
                Match(
                    bluesky_handle=bsky_handle,
                    bluesky_display_name=display_name,
                    mastodon_handle=bridgy_handle,
                    source="bridgy_fed",
                    verified="yes",
                )
            )

    return matches, len(follows)
