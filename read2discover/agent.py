from __future__ import annotations

import json
from urllib import request, error

from .config import setting
from .models import InterestPlan
from .text import keywords


class PlanningError(RuntimeError):
    pass


def keyword_plan(reading: str) -> InterestPlan:
    terms = keywords(reading, 8)
    if not terms:
        raise ValueError("Please paste enough reading material to identify at least one topic.")
    core = terms[:4]
    return InterestPlan(
        summary=f"Explore {', '.join(core)} and adjacent practical perspectives.",
        topics=tuple(core),
        youtube_query=" ".join(core[:3]) + " explained",
        hacker_news_query=" ".join(core[:3]),
        subtopics=tuple(terms[:6]),
        used_llm=False,
    )


def _extract_json(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise PlanningError("The model did not return a JSON object.")
    return json.loads(text[start : end + 1])


def plan_interests(reading: str, use_llm: bool = True) -> InterestPlan:
    fallback = keyword_plan(reading)
    api_key = setting("PARLEY_API_KEY")
    if not use_llm or not api_key:
        return fallback

    base = setting("PARLEY_BASE_URL", "https://parley.api.mit.edu/v1").rstrip("/")
    model = setting("PARLEY_MODEL", "gpt-5-mini")
    prompt = f"""Analyze the reading and return ONLY valid JSON with keys:
summary (one sentence), topics (3-5 concise strings), youtube_query (one query),
hacker_news_query (one query), subtopics (4-7 distinct discovery angles).
The YouTube query must be 4-8 words. The Hacker News query must be 2-4 words.
Queries must be specific but not quote the input. Do not add markdown.

READING:
{reading[:12000]}"""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You plan bounded, high-quality content discovery searches."},
            {"role": "user", "content": prompt},
        ],
        "max_completion_tokens": 1200,
    }
    req = request.Request(
        f"{base}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=35) as response:
            result = json.load(response)
        data = _extract_json(result["choices"][0]["message"]["content"])
        topics = tuple(str(x).strip() for x in data.get("topics", []) if str(x).strip())[:5]
        subtopics = tuple(str(x).strip() for x in data.get("subtopics", []) if str(x).strip())[:7]
        if len(topics) < 2 or len(subtopics) < 2:
            raise PlanningError("The model returned too few topics.")
        youtube_query = str(data.get("youtube_query") or fallback.youtube_query).strip()
        hacker_news_query = str(data.get("hacker_news_query") or fallback.hacker_news_query).strip()
        # HN's search works best with a compact phrase; long generated queries can
        # accidentally require every term and yield no results.
        if len(hacker_news_query.split()) > 4:
            hacker_news_query = topics[0]
        if len(youtube_query.split()) > 8:
            youtube_query = " ".join(youtube_query.split()[:8])
        return InterestPlan(
            summary=str(data.get("summary") or fallback.summary),
            topics=topics,
            youtube_query=youtube_query,
            hacker_news_query=hacker_news_query,
            subtopics=subtopics,
            used_llm=True,
        )
    except (error.URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError, PlanningError):
        return fallback

