"""Minimal client for the Hugging Face datasets-server API.

Used because our sandbox can reach huggingface.co / datasets-server.huggingface.co but not the
HF file CDN, nor the primary government hosts (sec.gov, ffiec.gov, ...). The `/filter` endpoint
runs a DuckDB WHERE clause server-side, so we can pull a single entity's records out of a
multi-GB mirror without downloading it.

Docs: https://huggingface.co/docs/dataset-viewer
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request

BASE = "https://datasets-server.huggingface.co"


def _get(path: str, params: dict, retries: int = 4) -> dict:
    url = f"{BASE}/{path}?{urllib.parse.urlencode(params)}"
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception:  # transient 5xx / timeouts are common on large configs
            if attempt == retries - 1:
                raise
            time.sleep(2 ** (attempt + 1))
    raise RuntimeError("unreachable")


def size(dataset: str) -> dict:
    return _get("size", {"dataset": dataset})


def rows(dataset: str, config: str, offset: int = 0, length: int = 100, split: str = "train") -> dict:
    return _get("rows", {"dataset": dataset, "config": config, "split": split,
                         "offset": offset, "length": length})


def filter_rows(dataset: str, config: str, where: str, orderby: str | None = None,
                limit: int = 1000, split: str = "train") -> tuple[list[dict], dict]:
    """Return up to `limit` rows matching `where` (DuckDB SQL), paging 100 at a time.

    Second element is response metadata (num_rows_total, partial flag).
    """
    out: list[dict] = []
    meta: dict = {}
    offset = 0
    while len(out) < limit:
        params = {"dataset": dataset, "config": config, "split": split, "where": where,
                  "offset": offset, "length": min(100, limit - len(out))}
        if orderby:
            params["orderby"] = orderby
        resp = _get("filter", params)
        meta = {"num_rows_total": resp.get("num_rows_total"), "partial": resp.get("partial")}
        batch = [r["row"] for r in resp.get("rows", [])]
        out.extend(batch)
        if len(batch) < params["length"]:
            break
        offset += len(batch)
    return out, meta
