#!/usr/bin/env python3
"""Update month/year strings across HTML files and sitemap.xml to the next month.

Intended to run on the last day of each month via GitHub Actions.
"""

import re
import sys
from datetime import date, timedelta
from pathlib import Path


def next_month(d: date) -> tuple[str, int]:
    """Return (month_name, year) for the month after d."""
    first_next = (d.replace(day=1) + timedelta(days=32)).replace(day=1)
    return first_next.strftime("%B"), first_next.year


def is_last_day_of_month(d: date) -> bool:
    next_day = d + timedelta(days=1)
    return next_day.month != d.month


HTML_FILES = [
    "index.html",
    "privacy.html",
    "terms.html",
    "beginners-guide.html",
    "rewards-guide.html",
    "event-codes.html",
]

MONTH_YEAR_RE = re.compile(r"[A-Z][a-z]+ 20\d\d")
DATE_RE = re.compile(r"20\d\d-\d{2}-\d{2}")


def update_html(path: Path, month: str, year: int) -> bool:
    text = path.read_text()
    new_text = MONTH_YEAR_RE.sub(f"{month} {year}", text)
    if new_text != text:
        path.write_text(new_text)
        return True
    return False


def update_json_ld_dates(path: Path, new_date: str) -> bool:
    text = path.read_text()
    new_text = re.sub(
        r'("datePublished"|"dateModified"): "20\d\d-\d{2}-\d{2}"',
        lambda m: f'{m.group(1)}: "{new_date}"',
        text,
    )
    if new_text != text:
        path.write_text(new_text)
        return True
    return False


def update_sitemap(path: Path, new_date: str) -> bool:
    text = path.read_text()
    lines = text.splitlines(keepends=True)
    result = []
    skip_first = True
    changed = False
    for line in lines:
        if "<lastmod>" in line and skip_first:
            # Skip homepage lastmod — managed by fetch-codes.yml
            skip_first = False
            result.append(line)
            continue
        if "<lastmod>" in line:
            new_line = DATE_RE.sub(new_date, line)
            if new_line != line:
                changed = True
            result.append(new_line)
        else:
            result.append(line)
    if changed:
        path.write_text("".join(result))
    return changed


def main() -> None:
    today = date.today()
    if not is_last_day_of_month(today):
        print(f"Today ({today}) is not the last day of the month. Nothing to do.")
        sys.exit(0)

    month, year = next_month(today)
    new_date = f"{year}-{list(__import__('calendar').month_name).index(month):02d}-01"
    print(f"Updating to: {month} {year} ({new_date})")

    root = Path(__file__).parent.parent
    changed_files = []

    for filename in HTML_FILES:
        path = root / filename
        if not path.exists():
            continue
        html_changed = update_html(path, month, year)
        date_changed = update_json_ld_dates(path, new_date)
        if html_changed or date_changed:
            changed_files.append(filename)
            print(f"  Updated: {filename}")

    sitemap = root / "sitemap.xml"
    if update_sitemap(sitemap, new_date):
        changed_files.append("sitemap.xml")
        print(f"  Updated: sitemap.xml")

    if not changed_files:
        print("No changes needed.")
    else:
        print(f"Done. {len(changed_files)} file(s) updated.")


if __name__ == "__main__":
    main()
