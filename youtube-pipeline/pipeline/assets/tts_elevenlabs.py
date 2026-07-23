"""ElevenLabs TTS stub.

Wire this up when you have an API key (ELEVENLABS_API_KEY / ELEVENLABS_VOICE_ID
in .env). Until then, `synthesize()` raises with a clear message and the rest of
the pipeline works without it — you can narrate manually and drop the audio into
renders/<slug>/narration.mp3 yourself.

Using TTS narration means the upload is flagged as altered/synthetic content
(config/settings.yml -> upload.default_synthetic).
"""

from __future__ import annotations

import os
from pathlib import Path

API_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


def synthesize(text: str, out_path: Path) -> Path:
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID")
    if not api_key or not voice_id:
        raise RuntimeError(
            "ElevenLabs not configured. Set ELEVENLABS_API_KEY and "
            "ELEVENLABS_VOICE_ID in .env, or record narration manually to "
            f"{out_path}."
        )
    import requests

    resp = requests.post(
        API_URL.format(voice_id=voice_id),
        headers={"xi-api-key": api_key, "content-type": "application/json"},
        json={
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        },
        timeout=300,
    )
    resp.raise_for_status()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(resp.content)
    return out_path
