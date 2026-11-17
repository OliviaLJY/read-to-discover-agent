from __future__ import annotations

import json
from datetime import datetime, timezone
from urllib import parse, request

from .config import setting
from .models import Candidate


def _get_json(url: str, timeout: int = 15) -> dict:
    req = request.Request(url, headers={"User-Agent": "Read2Discover/1.0"})
    with request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def search_hacker_news(query: str, limit: int = 12) -> list[Candidate]:
    params = parse.urlencode({"query": query, "tags": "story", "hitsPerPage": limit})
    data = _get_json(f"https://hn.algolia.com/api/v1/search?{params}")
    items: list[Candidate] = []
    for hit in data.get("hits", []):
        title = (hit.get("title") or "").strip()
        object_id = str(hit.get("objectID") or "")
        if not title or not object_id:
            continue
        story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}"
        discussion = f"https://news.ycombinator.com/item?id={object_id}"
        description = f"{hit.get('points', 0)} points · {hit.get('num_comments', 0)} comments · discussion: {discussion}"
        items.append(Candidate(title, story_url, "Hacker News", "article", description, hit.get("created_at", ""), hit.get("author", "")))
    return items


def search_youtube(query: str, limit: int = 12) -> tuple[list[Candidate], bool]:
    key = setting("YOUTUBE_API_KEY")
    if not key:
        return demo_youtube(query, limit), True
    params = parse.urlencode({
        "part": "snippet", "type": "video", "maxResults": min(limit, 25),
        "q": query, "key": key, "safeSearch": "moderate", "relevanceLanguage": "en",
    })
    data = _get_json(f"https://www.googleapis.com/youtube/v3/search?{params}")
    items = []
    for row in data.get("items", []):
        video_id = row.get("id", {}).get("videoId")
        snippet = row.get("snippet", {})
        if not video_id or not snippet.get("title"):
            continue
        items.append(Candidate(
            snippet["title"], f"https://www.youtube.com/watch?v={video_id}", "YouTube", "video",
            snippet.get("description", ""), snippet.get("publishedAt", ""), snippet.get("channelTitle", ""),
        ))
    return items, False


def demo_youtube(query: str, limit: int = 12) -> list[Candidate]:
    """Deterministic catalog used only when the official API key is absent."""
    topic = " ".join(query.split()[:4]).title() or "Research Topic"
    rows = [
        (f"{topic}: a visual introduction", "UCs_demo_intro"),
        (f"How {topic} works in practice", "UCs_demo_practice"),
        (f"The history and future of {topic}", "UCs_demo_future"),
        (f"A critical debate about {topic}", "UCs_demo_debate"),
        (f"{topic} case study and lessons", "UCs_demo_case"),
    ]
    return [Candidate(title, f"https://www.youtube.com/results?search_query={parse.quote_plus(title)}", "YouTube (demo)", "video", "Demo catalog item; add YOUTUBE_API_KEY for live video links.") for title, _ in rows[:limit]]

