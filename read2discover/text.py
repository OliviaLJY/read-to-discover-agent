from __future__ import annotations

import re
from collections import Counter

STOPWORDS = {
    "about", "after", "again", "also", "among", "and", "are", "because", "been", "being", "between",
    "but", "can", "could", "does", "for", "from", "have", "help", "into", "make", "more", "most", "other", "over", "such",
    "than", "that", "their", "there", "these", "they", "this", "through", "under", "using",
    "very", "what", "when", "where", "which", "while", "with", "would", "your", "were",
    "will", "each", "some", "only", "then", "them", "those", "reading", "article", "book",
}


def tokens(text: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9+.-]{2,}", text)]


def keywords(text: str, limit: int = 8) -> list[str]:
    counts = Counter(t for t in tokens(text) if t not in STOPWORDS and not t.isdigit())
    first_pos = {term: tokens(text).index(term) for term in counts}
    return [k for k, _ in sorted(counts.items(), key=lambda kv: (-kv[1], first_pos[kv[0]]))[:limit]]


def overlap(a: str, terms: list[str] | tuple[str, ...]) -> tuple[float, list[str]]:
    haystack = set(tokens(a))
    normalized = [t.lower() for t in terms if t]
    matched = []
    for term in normalized:
        meaningful = [part for part in tokens(term) if part not in STOPWORDS]
        if meaningful and any(part in haystack for part in meaningful):
            matched.append(term)
    return (len(matched) / max(1, len(normalized))), matched

