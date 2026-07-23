"""OAuth 2.0 for the YouTube Data + Analytics APIs, with refresh-token handling.

First run opens a browser consent flow and stores the token (including the
refresh token) at YT_TOKEN_FILE. Subsequent runs refresh silently.

IMPORTANT: your Google Cloud OAuth consent screen must be set to "In production"
— in "Testing" mode refresh tokens expire after 7 days and the pipeline will
demand a re-auth weekly. See README.md § YouTube API setup.
"""

from __future__ import annotations

import os
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
]


def _token_file() -> Path:
    return Path(os.environ.get("YT_TOKEN_FILE", "data/token.json"))


def _client_secrets_file() -> Path:
    return Path(os.environ.get("YT_CLIENT_SECRETS_FILE", "client_secret.json"))


def get_credentials():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    token_file = _token_file()
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            secrets = _client_secrets_file()
            if not secrets.exists():
                raise FileNotFoundError(
                    f"{secrets} not found. Download OAuth client secrets from Google "
                    "Cloud Console (see README § YouTube API setup) and set "
                    "YT_CLIENT_SECRETS_FILE in .env."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(secrets), SCOPES)
            # access_type=offline + consent prompt => Google returns a refresh token.
            creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(creds.to_json())
    return creds


def youtube_service():
    from googleapiclient.discovery import build

    return build("youtube", "v3", credentials=get_credentials())


def analytics_service():
    from googleapiclient.discovery import build

    return build("youtubeAnalytics", "v2", credentials=get_credentials())
