from __future__ import annotations

import html
import json
import math
import re
from urllib import parse, request


def _language_for(query: str) -> str:
    return "zh" if re.search(r"[\u3400-\u9fff]", query) else "en"


def _get_json(url: str) -> dict:
    req = request.Request(url, headers={"User-Agent": "Read2Discover/1.0 (educational prototype)"})
    with request.urlopen(req, timeout=15) as response:
        return json.load(response)


def _plain_snippet(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", value))).strip()


def estimate_read_time(paragraphs: list[str], language: str = "en") -> str:
    displayed_text = " ".join(paragraphs)
    if language == "zh":
        characters = len(re.findall(r"[\u3400-\u9fff]", displayed_text))
        minutes = max(1, math.ceil(characters / 400))
        return f"约 {minutes} 分钟"
    words = len(re.findall(r"\b[\w'-]+\b", displayed_text))
    minutes = max(1, math.ceil(words / 220))
    return f"{minutes} min read"


def search_articles(query: str, limit: int = 6) -> list[dict]:
    query = query.strip()
    if len(query) < 2:
        raise ValueError("Enter at least two characters to search.")
    language = _language_for(query)
    params = parse.urlencode({
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": min(limit, 10),
        "utf8": 1,
        "format": "json",
    })
    data = _get_json(f"https://{language}.wikipedia.org/w/api.php?{params}")
    return [
        {
            "pageid": int(row["pageid"]),
            "title": row["title"],
            "snippet": _plain_snippet(row.get("snippet", "")),
            "language": language,
        }
        for row in data.get("query", {}).get("search", [])
        if row.get("pageid") and row.get("title")
    ]


def fetch_article(pageid: int, language: str = "en") -> dict:
    params = parse.urlencode({
        "action": "query",
        "prop": "extracts|info",
        "pageids": int(pageid),
        "explaintext": 1,
        "exsectionformat": "plain",
        "inprop": "url",
        "format": "json",
    })
    data = _get_json(f"https://{language}.wikipedia.org/w/api.php?{params}")
    page = data.get("query", {}).get("pages", {}).get(str(pageid), {})
    extract = page.get("extract", "")
    raw_paragraphs = [re.sub(r"\s+", " ", part).strip() for part in extract.split("\n")]
    paragraphs = [part for part in raw_paragraphs if len(part) >= 60 and not part.startswith("==")]
    if len(paragraphs) < 2:
        raise ValueError("This result does not contain enough readable article text.")
    deck = paragraphs[0]
    body = paragraphs[1:9] or paragraphs
    return {
        "section": "Search · Wikipedia" if language == "en" else "搜索 · 维基百科",
        "title": page.get("title") or "Untitled article",
        "deck": deck,
        "author": "Wikipedia contributors" if language == "en" else "维基百科贡献者",
        "date": "Knowledge article" if language == "en" else "知识文章",
        "read_time": estimate_read_time([deck, *body], language),
        "accent": "#8a5db0",
        "paragraphs": body,
        "source_url": page.get("fullurl", ""),
    }

