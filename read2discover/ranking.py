from __future__ import annotations

from urllib.parse import urlparse

from .models import Candidate, InterestPlan
from .text import overlap


def _valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _short_label(value: str, limit: int = 9) -> str:
    words = value.strip().split()
    return " ".join(words[:limit]) + ("…" if len(words) > limit else "")


def deduplicate(items: list[Candidate]) -> list[Candidate]:
    seen: set[str] = set()
    output = []
    for item in items:
        key = " ".join(item.title.lower().split())
        parsed = urlparse(item.url)
        domain_path = parsed.netloc.lower() + parsed.path.rstrip("/") + (f"?{parsed.query}" if parsed.query else "")
        if not _valid_url(item.url) or key in seen or domain_path in seen:
            continue
        seen.update({key, domain_path})
        output.append(item)
    return output


def rank(items: list[Candidate], plan: InterestPlan, limit: int = 5) -> list[Candidate]:
    terms = list(plan.topics) + list(plan.subtopics) + [plan.youtube_query, plan.hacker_news_query]
    for item in items:
        text = f"{item.title} {item.description}"
        rel, matched = overlap(text, terms)
        item.relevance = rel
        item.matched_terms = matched
        item.subtopic = max(plan.subtopics, key=lambda s: overlap(text, [s])[0], default="general")
        item.score = rel + (0.08 if item.source.startswith("YouTube") else 0.06)

    all_items = deduplicate(items)
    relevant_items = [item for item in all_items if item.relevance > 0]
    # Prefer a fully relevant pool when it can still fill the feed. Sparse
    # searches may retain zero-score items so the UI can degrade gracefully.
    pool = sorted(relevant_items if len(relevant_items) >= limit else all_items, key=lambda item: (-item.score, item.title.lower()))
    chosen: list[Candidate] = []
    sources: set[str] = set()
    source_counts: dict[str, int] = {}
    subtopics: set[str] = set()
    available_sources = {item.source.split(" ")[0] for item in pool}
    available_counts = {
        source: sum(item.source.split(" ")[0] == source for item in pool)
        for source in available_sources
    }
    min_per_source = 2 if len(available_sources) >= 2 and limit >= 4 and all(count >= 2 for count in available_counts.values()) else 1
    while pool and len(chosen) < limit:
        remaining_slots = limit - len(chosen)
        needed = sum(max(0, min_per_source - source_counts.get(source, 0)) for source in available_sources)
        eligible = pool
        if remaining_slots <= needed:
            eligible = [item for item in pool if source_counts.get(item.source.split(" ")[0], 0) < min_per_source]
        best = max(
            eligible,
            key=lambda item: item.score
            + (0.18 if item.source.split(" ")[0] not in sources else 0)
            + (0.14 if item.subtopic not in subtopics else 0),
        )
        pool.remove(best)
        best.score += (0.18 if best.source.split(" ")[0] not in sources else 0) + (0.14 if best.subtopic not in subtopics else 0)
        match = _short_label(best.matched_terms[0] if best.matched_terms else plan.topics[0], 7)
        angle = _short_label(best.subtopic, 10)
        article = "An" if best.format[:1].lower() in "aeiou" else "A"
        if match.lower() in angle.lower() or angle.lower() in match.lower():
            best.explanation = f"{article} {best.format} that takes the article's {match} theme into a concrete example."
        else:
            best.explanation = f"{article} {best.format} that builds on {match}, with a closer look at {angle}."
        chosen.append(best)
        source_key = best.source.split(" ")[0]
        sources.add(source_key)
        source_counts[source_key] = source_counts.get(source_key, 0) + 1
        subtopics.add(best.subtopic)
    return chosen


def keyword_baseline(items: list[Candidate], reading: str, limit: int = 5) -> list[Candidate]:
    from .text import keywords
    terms = keywords(reading, 8)
    scored = []
    for item in deduplicate(items):
        item.relevance, item.matched_terms = overlap(f"{item.title} {item.description}", terms)
        scored.append(item)
    return sorted(scored, key=lambda item: (-item.relevance, item.title.lower()))[:limit]

