"""YouTube helper for workflow research: search, metadata, and timestamped transcripts.

  python3 yt_tool.py search "municipal credit analysis ACFR" [n]
  python3 yt_tool.py meta <video_id>            # title, channel, duration, date, description, chapters
  python3 yt_tool.py transcript <video_id>      # cleaned auto-captions, one line per ~30 s with [mm:ss]

Search parses the public results page; metadata and captions come from yt-dlp (the official
transcript endpoint blocks cloud IPs, yt-dlp's caption download does not). Transcripts are
cached under $YT_CACHE (default /tmp/yt_cache).
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

CACHE = pathlib.Path(os.environ.get("YT_CACHE", "/tmp/yt_cache"))
UA = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}


def search(query: str, n: int = 10) -> list[dict]:
    url = ("https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
           + "&hl=en&gl=US")
    html = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", html.decode("utf-8", "ignore"))
    if not m:
        return []
    out: list[dict] = []

    def walk(o):
        if isinstance(o, dict):
            v = o.get("videoRenderer")
            if v:
                out.append({
                    "id": v.get("videoId"),
                    "url": f"https://www.youtube.com/watch?v={v.get('videoId')}",
                    "title": "".join(r.get("text", "") for r in v.get("title", {}).get("runs", [])),
                    "channel": "".join(r.get("text", "") for r in v.get("ownerText", {}).get("runs", [])),
                    "length": v.get("lengthText", {}).get("simpleText"),
                    "views": v.get("viewCountText", {}).get("simpleText"),
                    "published": v.get("publishedTimeText", {}).get("simpleText"),
                })
            for x in o.values():
                walk(x)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(json.loads(m.group(1)))
    return out[:n]


def _ytdlp(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["yt-dlp", "--no-warnings", "--skip-download", *args],
                          capture_output=True, text=True, timeout=180)


def meta(video_id: str) -> dict:
    d = None
    for attempt in range(3):  # yt-dlp occasionally returns nothing under rate limiting
        p = _ytdlp(["-J", f"https://www.youtube.com/watch?v={video_id}"])
        try:
            d = json.loads(p.stdout)
        except json.JSONDecodeError:
            d = None
        if d:
            break
        time.sleep(3 * (attempt + 1))
    if not d:
        return {"id": video_id, "error": (p.stderr or "no metadata")[-300:]}
    return {
        "id": video_id, "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": d.get("title"), "channel": d.get("channel"),
        "duration": d.get("duration_string"), "upload_date": d.get("upload_date"),
        "views": d.get("view_count"),
        "chapters": [f"[{int(c['start_time'] // 60):02d}:{int(c['start_time'] % 60):02d}] {c['title']}"
                     for c in (d.get("chapters") or [])],
        "description": (d.get("description") or "")[:4000],
    }


def _vtt_to_lines(vtt: str, every: int = 30) -> list[str]:
    """Collapse rolling auto-caption cues into plain text, bucketed by `every` seconds.

    Each auto-caption cue repeats the previous cue's line and adds one new line, so only the
    last line of each cue is new.
    """
    lines, bucket, start, prev = [], [], None, None
    for block in vtt.split("\n\n"):
        m = re.search(r"(\d+):(\d+):(\d+)\.\d+ -->", block)
        if not m:
            continue
        t = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
        text_lines = [re.sub(r"<[^>]+>", "", l).strip() for l in block.split("\n")[1:]
                      if "-->" not in l]
        text_lines = [l for l in text_lines if l]
        if not text_lines or text_lines[-1] == prev:
            continue
        prev = text_lines[-1]
        if start is None:
            start = t
        bucket.append(prev)
        if t - start >= every:
            lines.append(f"[{start // 60:02d}:{start % 60:02d}] " + " ".join(bucket))
            bucket, start = [], None
    if bucket:
        lines.append(f"[{(start or 0) // 60:02d}:{(start or 0) % 60:02d}] " + " ".join(bucket))
    return lines


def transcript(video_id: str) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f"{video_id}.txt"
    if out.exists():
        return out.read_text()
    _ytdlp(["--write-auto-subs", "--write-subs", "--sub-langs", "en.*,en", "--sub-format", "vtt",
            "-o", str(CACHE / "%(id)s"), f"https://www.youtube.com/watch?v={video_id}"])
    vtts = sorted(CACHE.glob(f"{video_id}*.vtt"))
    if not vtts:
        return ""
    text = "\n".join(_vtt_to_lines(vtts[0].read_text(errors="ignore")))
    out.write_text(text)
    time.sleep(1)  # be polite; YouTube rate-limits bursts
    return text


if __name__ == "__main__":
    cmd, arg = sys.argv[1], sys.argv[2]
    if cmd == "search":
        for r in search(arg, int(sys.argv[3]) if len(sys.argv) > 3 else 10):
            print(json.dumps(r))
    elif cmd == "meta":
        print(json.dumps(meta(arg), indent=2))
    elif cmd == "transcript":
        print(transcript(arg))
