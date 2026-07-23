"""Resumable upload (videos.insert) with publishAt scheduling.

Only called by the review CLI for APPROVED queue items — the human gate is
upstream and nothing reaches this module without passing it. Sets:
  - snippet: title, description, tags, categoryId
  - status: private + publishAt (scheduled), selfDeclaredMadeForKids,
    containsSyntheticMedia (YouTube's "altered or synthetic content" disclosure)
"""

from __future__ import annotations

import time

from .. import paths
from . import quota
from .auth import youtube_service


def upload_video(item: dict, video_file: str, publish_at_iso: str, confirm=None) -> str:
    """Upload a queue item's video. Returns the YouTube video ID.

    `publish_at_iso` must be an RFC3339 UTC timestamp (e.g. 2026-08-01T15:00:00Z).
    """
    if item.get("status") != "approved":
        raise PermissionError(
            f"refusing to upload {item.get('slug')!r}: status is "
            f"{item.get('status')!r}, not 'approved'. Nothing publishes without "
            "passing the human review gate."
        )

    from googleapiclient.errors import HttpError, ResumableUploadError
    from googleapiclient.http import MediaFileUpload

    meta = item["metadata"]
    up_cfg = paths.settings()["upload"]
    body = {
        "snippet": {
            "title": meta["title"],
            "description": meta["description"],
            "tags": meta["tags"],
            "categoryId": meta.get("category_id", "27"),
        },
        "status": {
            "privacyStatus": up_cfg["privacy_before_publish"],
            "publishAt": publish_at_iso,
            "selfDeclaredMadeForKids": up_cfg["made_for_kids"],
            # YouTube's altered/synthetic content disclosure — required when the
            # video uses realistic AI-generated voice or imagery.
            "containsSyntheticMedia": bool(item.get("synthetic", True)),
        },
    }

    quota.charge("videos.insert", confirm=confirm)
    yt = youtube_service()
    media = MediaFileUpload(video_file, chunksize=8 * 1024 * 1024, resumable=True)
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    backoff = 2
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"  upload {int(status.progress() * 100)}%")
            backoff = 2
        except (HttpError, ResumableUploadError) as e:
            retriable = getattr(e, "resp", None) is not None and e.resp.status in (
                500, 502, 503, 504,
            )
            if not retriable or backoff > 64:
                raise
            print(f"  transient error ({e.resp.status}), retrying in {backoff}s")
            time.sleep(backoff)
            backoff *= 2

    video_id = response["id"]
    print(f"  uploaded: https://youtu.be/{video_id} (scheduled for {publish_at_iso})")
    return video_id
