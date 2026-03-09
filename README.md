# GenshinCo.de

A static site listing active Genshin Impact redeem codes. Codes are fetched automatically every 6 hours and committed to the repo, so the GitHub Pages site always serves fresh data with no backend.

## How it works

1. A GitHub Actions workflow runs `scripts/fetch_codes.py` on a 6-hour schedule.
2. The script fetches active codes from the [hoyo-codes API](https://hoyo-codes.seria.moe/codes?game=genshin).
3. If `codes.json` changed, the bot commits the updated file to `main`.
4. `index.html` fetches `codes.json` at page load and renders each code as a card.

## Triggering the workflow manually

Go to **Actions** → **Fetch Genshin Codes** → **Run workflow**.

## Adding a code manually

Edit `codes.json` and add an entry with `"source": "manual"`:

```json
[
  {
    "code": "MYCODE123",
    "rewards": "60 Primogems + 10,000 Mora",
    "source": "manual"
  }
]
```

Manual entries are preserved across automated runs as long as their code does not appear in the API response.

## codes.json schema

```json
[
  {
    "code": "ABC123",
    "rewards": "Primogem x60",
    "source": "hoyo-codes | manual"
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Redeem code (6–16 uppercase alphanumeric characters) |
| `rewards` | string | Human-readable reward description |
| `source` | string | `"hoyo-codes"` for API-fetched, `"manual"` for hand-added |
