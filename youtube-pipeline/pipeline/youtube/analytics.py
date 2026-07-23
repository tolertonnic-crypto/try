"""YouTube Analytics API pulls -> local CSV.

Pulls per-video metrics into data/analytics/videos_<date>.csv. Core metrics are
always requested; revenue metrics (RPM once you're in YPP) are attempted and
dropped gracefully if the channel isn't monetized yet. Impressions CTR is not
exposed by the Analytics API (it's Studio-only) — retention + views are the
proxies here; check Studio for thumbnail CTR.

Analytics API calls don't consume Data API quota, but the video listing does
(videos.list, 1 unit) — recorded in the ledger like everything else.
"""

from __future__ import annotations

import csv
import datetime as dt

from .. import paths
from . import quota
from .auth import analytics_service, youtube_service

CORE_METRICS = [
    "views",
    "estimatedMinutesWatched",
    "averageViewDuration",
    "averageViewPercentage",
    "subscribersGained",
]
REVENUE_METRICS = ["estimatedRevenue", "playbackBasedCpm"]


def _my_upload_ids(limit: int = 50) -> list[dict]:
    """List recent uploads [{id, title, publishedAt}] via the uploads playlist."""
    yt = youtube_service()
    quota.charge("channels.list")
    channels = yt.channels().list(part="contentDetails", mine=True).execute()
    uploads_playlist = channels["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    videos, page_token = [], None
    while len(videos) < limit:
        quota.charge("playlistItems.list")
        resp = yt.playlistItems().list(
            part="contentDetails,snippet", playlistId=uploads_playlist,
            maxResults=min(50, limit - len(videos)), pageToken=page_token,
        ).execute()
        videos += [
            {
                "id": it["contentDetails"]["videoId"],
                "title": it["snippet"]["title"],
                "publishedAt": it["contentDetails"].get("videoPublishedAt", ""),
            }
            for it in resp.get("items", [])
        ]
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return videos


def pull(days: int = 28) -> str:
    """Pull per-video analytics for the trailing window. Returns the CSV path."""
    from googleapiclient.errors import HttpError

    paths.ensure_dirs()
    end = dt.date.today()
    start = end - dt.timedelta(days=days)
    videos = _my_upload_ids()
    if not videos:
        raise RuntimeError("channel has no uploads yet")

    analytics = analytics_service()
    metrics = CORE_METRICS + REVENUE_METRICS

    def query(metric_list):
        return analytics.reports().query(
            ids="channel==MINE",
            startDate=start.isoformat(),
            endDate=end.isoformat(),
            metrics=",".join(metric_list),
            dimensions="video",
            filters="video==" + ",".join(v["id"] for v in videos[:200]),
            maxResults=200,
        ).execute()

    try:
        result = query(metrics)
    except HttpError:
        # Channel not monetized yet -> revenue metrics rejected; fall back.
        metrics = CORE_METRICS
        result = query(metrics)

    by_id = {row[0]: row[1:] for row in result.get("rows", [])}
    out = paths.ANALYTICS_DIR / f"videos_{end.isoformat()}.csv"
    with open(out, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["video_id", "title", "published_at", *metrics])
        for v in videos:
            writer.writerow([v["id"], v["title"], v["publishedAt"],
                             *by_id.get(v["id"], [""] * len(metrics))])
    print(f"wrote {out}")
    return str(out)
