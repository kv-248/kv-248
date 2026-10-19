# Analyst workflows on video

Web view: https://claude.ai/artifact/TmgaT9fedrnJK8ZXNDCVRJ

`videos_all.json` holds 71 YouTube videos of finance practitioners. Each record carries the source
documents used, the deliverable, timestamped steps, checks and judgment calls, all read from the
video's auto-captions (fetched with `poc/yt_tool.py`). Fit: A = full chain (source docs → workbook →
deliverable), B = a substantial part, C = concept only.

Reference level: BIWS "3-Statement Model: 90-Minute Case Study from a Blank Excel Sheet"
(https://www.youtube.com/watch?v=O2uPNfErmJo), re-checked line by line against its transcript.

Coverage: funds (22) and public sector (23) complete; corporate (18) and credit (8) stopped early.
`notes_funds.md` and `notes_public.md` hold the per-cluster synthesis and gaps.
