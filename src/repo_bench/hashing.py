"""Stable content hashing — the basis of `view_id` determinism.

Vendored verbatim from the spotlights-engine `signal_pipeline.layout` module
so this tool stands alone. The canonicalization rules are **pinned**: changing
them changes every `view_id` ever computed, which would silently invalidate
existing run dirs and the example match reports that cite them.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel


def _canonicalize(payload: Any) -> str:
    """Produce the exact string fed to SHA-256.

    Rules (pinned — manifests are only valid under these rules):
    1. Pydantic models → `model_dump(mode="json", by_alias=True, exclude_none=False)`.
       Lists of models map element-wise. Plain dicts/lists pass through.
    2. JSON-encode with `sort_keys=True, ensure_ascii=False, separators=(",", ":")`.
       No indentation, no trailing newline, deterministic key order.
    3. List order is preserved — a deliberate reorder forces fan-out re-evaluation.
    """
    if isinstance(payload, BaseModel):
        obj: Any = payload.model_dump(mode="json", by_alias=True, exclude_none=False)
    elif isinstance(payload, list):
        obj = [
            p.model_dump(mode="json", by_alias=True, exclude_none=False)
            if isinstance(p, BaseModel)
            else p
            for p in payload
        ]
    elif isinstance(payload, dict):
        obj = {
            k: (
                v.model_dump(mode="json", by_alias=True, exclude_none=False)
                if isinstance(v, BaseModel)
                else v
            )
            for k, v in payload.items()
        }
    else:
        obj = payload
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def artifact_hash(payload: Any) -> str:
    """Stable SHA-256 hex digest of an artifact's logical content."""
    return hashlib.sha256(_canonicalize(payload).encode("utf-8")).hexdigest()


__all__ = ["artifact_hash"]
