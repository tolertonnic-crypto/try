"""FFmpeg assembly stub.

Stitches narration audio + B-roll clips into a final MP4. This is deliberately
minimal — a faceless-channel edit usually deserves a human pass in an editor,
but this produces a publishable rough cut: clips concatenated and trimmed to the
narration length, narration as the audio track.

Expected layout (produced by the TTS + Pexels steps, or dropped in manually):
    renders/<slug>/narration.mp3
    renders/<slug>/broll/*.mp4      (ordered by filename)
Output:
    renders/<slug>/final.mp4
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .. import paths


def assemble(slug: str) -> Path:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg not found on PATH — install it or edit manually")

    workdir = paths.RENDERS_DIR / slug
    narration = workdir / "narration.mp3"
    broll = sorted((workdir / "broll").glob("*.mp4"))
    if not narration.exists():
        raise FileNotFoundError(f"{narration} missing — run TTS or record narration first")
    if not broll:
        raise FileNotFoundError(f"no clips in {workdir/'broll'} — fetch B-roll first")

    concat_list = workdir / "concat.txt"
    concat_list.write_text("".join(f"file '{c.resolve()}'\n" for c in broll))
    out = workdir / "final.mp4"
    # Concat b-roll, overlay narration, stop at the shorter of the two (-shortest),
    # normalize to 1080p30 with letterboxing.
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-i", str(narration),
        "-map", "0:v:0", "-map", "1:a:0",
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
               "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(out),
    ]
    subprocess.run(cmd, check=True)
    return out
