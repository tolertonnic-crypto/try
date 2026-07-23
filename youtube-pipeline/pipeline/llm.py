"""Thin wrapper around the Anthropic SDK.

All generation goes through `generate_json()`, which uses structured outputs
(`output_config.format` with a JSON schema) so responses parse reliably, and
streams so long scripts don't hit HTTP timeouts.

Tests and --dry-run inject a fake client via `set_client()` — nothing in the
pipeline requires network access until you actually generate.
"""

from __future__ import annotations

import json

from . import paths

_client = None

# When True, generate_json() returns schema-shaped placeholder data instead of
# calling the API — lets the whole pipeline be exercised with no keys at all.
DRY_RUN = False


def _stub_from_schema(schema: dict, name: str = "value"):
    if "enum" in schema:
        return schema["enum"][0]
    t = schema.get("type")
    if t == "object":
        return {k: _stub_from_schema(v, k) for k, v in schema.get("properties", {}).items()}
    if t == "array":
        return [_stub_from_schema(schema["items"], name)]
    if t == "string":
        return f"[dry-run] {name}"
    if t in ("integer", "number"):
        return 0
    if t == "boolean":
        return False
    return None


def set_client(client) -> None:
    """Inject a client (tests, dry-run). Pass None to reset to the real SDK client."""
    global _client
    _client = client


def _get_client():
    global _client
    if _client is None:
        from anthropic import Anthropic  # imported lazily so tests never need the SDK

        _client = Anthropic()
    return _client


def generate_json(system: str, prompt: str, schema: dict, max_tokens: int = 32000) -> dict:
    """One structured-output generation. Returns the parsed JSON object."""
    if DRY_RUN:
        return _stub_from_schema(schema, "root")
    client = _get_client()
    model = paths.settings()["generation"]["model"]
    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        thinking={"type": "adaptive"},
        system=system,
        messages=[{"role": "user", "content": prompt}],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    ) as stream:
        message = stream.get_final_message()

    if message.stop_reason == "max_tokens":
        raise RuntimeError("generation hit max_tokens — output is truncated; raise max_tokens")

    text = "".join(block.text for block in message.content if block.type == "text")
    return json.loads(text)
