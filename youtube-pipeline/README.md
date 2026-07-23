# YouTube Faceless Channel Pipeline — History / Micro-History

A **semi-automated** content pipeline: Claude generates scripts and metadata,
asset stubs handle voice/B-roll/assembly, and the YouTube Data API handles
scheduled uploads — but **nothing publishes without passing the human review
gate**. Monetization: YPP ad revenue + affiliate links (UTM-attributed, with
FTC disclosure enforced in code).

```
backlog ─▶ generate ─▶ metadata ─▶ [HUMAN REVIEW GATE] ─▶ upload (scheduled)
   ▲                                      │                     │
   └── weekly summary ◀── analytics ◀─────┴─────────────────────┘
```

## Layout

| Path | What |
|---|---|
| `style-guide.md` | Brand voice + visual identity. **Read into every generation prompt** — edit it and the next video follows. |
| `content-strategy.md` | 5 pillars, audience, cadence, pillar→affiliate mapping. |
| `originality-checklist.md` | Per-video editorial requirements shown at review. |
| `backlog/topics.yml` | Topic backlog (unused/queued/used/rejected). |
| `config/settings.yml` | Model, schedule slots, quota costs, upload flags. |
| `config/links.yml` | Affiliate link registry + FTC disclosure text. |
| `pipeline/` | The code (see module docstrings). |
| `review/` | The queue: `queue/` → `approved/` or `rejected/`. |
| `data/` | Local state: quota ledger, structure history, analytics CSVs. |

## Setup

```bash
cd youtube-pipeline
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env         # fill in keys
```

## Daily workflow

```bash
python cli.py backlog add "Why did sailors get scurvy for 400 years?" \
    --angle "The cure was found, lost, and found again — twice" \
    --pillar myths-vs-records

python cli.py generate            # next unused topic -> script in review/queue/
python cli.py metadata <slug>     # titles/description/tags + affiliate links
# ...produce the video (TTS/B-roll/ffmpeg stubs in pipeline/assets/, or edit manually)
python cli.py review              # THE GATE: checklist, approve/edit/reject, assign slot
python cli.py upload <slug> final.mp4   # approved items only; scheduled via publishAt
python cli.py analytics && python cli.py weekly
```

## YouTube API setup (read this once, carefully)

1. **Create a Google Cloud project** at console.cloud.google.com.
2. **Enable APIs**: "YouTube Data API v3" and "YouTube Analytics API"
   (APIs & Services → Library).
3. **Configure the OAuth consent screen** (APIs & Services → OAuth consent screen):
   - User type: *External*.
   - Add the scopes for YouTube upload/readonly and yt-analytics.
   - Add your Google account as a test user *for now*.
4. **Create credentials**: Credentials → Create Credentials → OAuth client ID →
   *Desktop app*. Download the JSON as `client_secret.json` into this directory
   (path configurable via `YT_CLIENT_SECRETS_FILE` in `.env`).
5. **Publish the app ("In production")** — this is the step people skip and then
   wonder why automation breaks: while the consent screen is in **Testing** mode,
   Google expires refresh tokens after **7 days**, so the pipeline would demand a
   browser re-auth every week. Switching the app to **In production** (no
   verification needed for your own private use of these scopes — you'll just see
   an "unverified app" warning on first consent) makes refresh tokens long-lived.
6. First `python cli.py upload ...` opens a browser once; the token (with refresh
   token) is stored at `data/token.json` and refreshed automatically after that.

### Quota

The Data API gives 10,000 units/day by default. Costs are configured in
`config/settings.yml` (`quota.costs`) — as documented by Google, `videos.insert`
is **1600 units** and `search.list` is 100, so the pipeline avoids `search.list`
entirely (video listing goes through the 1-unit `playlistItems.list`) and caches
Pexels/analytics results locally. Every call is recorded in `data/quota_ledger.json`
(resets midnight Pacific, like Google's quota); `python cli.py quota` shows usage,
and any operation ≥ `quota.warn_at_units` asks for confirmation first. If Google
revises unit costs, update `settings.yml` — nothing is hard-coded.

### Altered/synthetic content disclosure

Uploads set `status.containsSyntheticMedia` from the queue item's `synthetic`
field (default `true` while the TTS stub is in use — change
`upload.default_synthetic` in `settings.yml` if you narrate yourself and use only
real footage). The review CLI displays the flag on every item.

## The human review gate (non-negotiable)

- `generate`/`metadata` only ever *stage* items in `review/queue/`.
- `python cli.py review` shows the script, similarity report vs the last 20
  videos, every factual claim (with confidence + where to verify), the exact
  description that will publish, and the originality checklist.
- Approval requires typing confirmation that the checklist is satisfied and a
  review note; the item then gets the next open schedule slot.
- `upload.py` **refuses** any item whose status isn't `approved` — there is no
  code path that publishes without the gate.

## Tracking

- `python cli.py analytics` → per-video CSV (views, watch time, retention;
  revenue metrics appear automatically once the channel is in YPP). Impressions
  CTR isn't exposed by the Analytics API — check Studio for thumbnail CTR.
- Affiliate links carry `utm_campaign=<video-slug>`; export click data from your
  affiliate dashboards to `data/affiliate_clicks.csv`
  (`utm_campaign,clicks,conversions`) and `python cli.py weekly` joins it with
  analytics to report per-pillar performance and suggest next week's emphasis.

## Guardrails

- No view botting, engagement automation, comment spam, or fake-activity
  features — not implemented, and don't ask the pipeline to.
- Scripts list every checkable factual claim; the checklist requires human
  verification against sources outside the generator.
- FTC affiliate disclosure is enforced in `metadata_generator.build_description`
  (it raises rather than emit links without a disclosure) and covered by tests.

## Tests

```bash
python -m pytest tests/ -q
```

Tests cover the backlog state machine, similarity flagging, FTC/UTM enforcement,
the quota ledger, and the review gate (including that unapproved items cannot be
uploaded). LLM calls are faked — no network or API keys needed.
