#!/usr/bin/env python3
"""Fetch active Genshin Impact codes from hoyo-codes API and update codes.json."""

import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

API_URL = "https://hoyo-codes.seria.moe/codes?game=genshin"
CODES_JSON = Path(__file__).parent.parent / "codes.json"
MAX_RESPONSE_BYTES = 100 * 1024  # 100KB
MAX_CODES = 10
CODE_PATTERN = re.compile(r'^[A-Z0-9]{6,16}$')
MAX_REWARDS_LEN = 200
HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
SOURCE_HOYO = "hoyo-codes"
SOURCE_MANUAL = "manual"


def sanitize_rewards(text: str) -> str:
    text = HTML_TAG_PATTERN.sub('', str(text)).strip()
    if len(text) > MAX_REWARDS_LEN:
        print(f"WARNING: rewards text truncated (was {len(text)} chars)", file=sys.stderr)
        text = text[:MAX_REWARDS_LEN]
    return text


def fetch_codes() -> list[dict]:
    req = urllib.request.Request(API_URL, headers={"User-Agent": "genshinco.de/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected
            raw = resp.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                print("ERROR: API response exceeds 100KB limit", file=sys.stderr)
                sys.exit(1)
            data = json.loads(raw)
    except urllib.error.URLError as e:
        print(f"ERROR: Failed to fetch codes: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON response: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, dict) or not isinstance(data.get("codes"), list):
        print("ERROR: Unexpected API response schema", file=sys.stderr)
        sys.exit(1)

    valid = []
    for entry in data["codes"]:
        if not isinstance(entry, dict):
            print(f"WARNING: skipping non-dict entry: {entry!r}", file=sys.stderr)
            continue
        code = entry.get("code", "")
        if not isinstance(code, str) or not CODE_PATTERN.match(code):
            print(f"WARNING: skipping invalid code: {code!r}", file=sys.stderr)
            continue
        rewards_raw = entry.get("rewards") or entry.get("reward") or ""
        if isinstance(rewards_raw, list):
            rewards_raw = ", ".join(str(r) for r in rewards_raw)
        rewards = sanitize_rewards(rewards_raw)
        valid.append({"code": code, "rewards": rewards, "source": SOURCE_HOYO})
        if len(valid) >= MAX_CODES:
            print(f"WARNING: capped at {MAX_CODES} codes", file=sys.stderr)
            break

    return valid


def load_existing() -> list[dict]:
    if not CODES_JSON.exists():
        return []
    try:
        data = json.loads(CODES_JSON.read_text())
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError) as e:
        print(f"WARNING: could not read existing codes.json: {e}", file=sys.stderr)
    return []


def merge(existing: list[dict], fetched: list[dict]) -> list[dict]:
    manual = [e for e in existing if e.get("source") == SOURCE_MANUAL]
    api_codes = {e["code"] for e in fetched}
    # Keep manual codes not overridden by API
    result = [m for m in manual if m["code"] not in api_codes]
    result.extend(fetched)
    return result


def main():
    fetched = fetch_codes()
    if not fetched:
        print("WARNING: API returned 0 valid codes — keeping existing codes.json unchanged", file=sys.stderr)
        sys.exit(0)

    existing = load_existing()
    merged = merge(existing, fetched)
    CODES_JSON.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n")
    print(f"OK: wrote {len(merged)} codes to {CODES_JSON}")


if __name__ == "__main__":
    main()
