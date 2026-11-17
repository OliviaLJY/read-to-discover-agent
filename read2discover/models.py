from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class InterestPlan:
    summary: str
    topics: tuple[str, ...]
    youtube_query: str
    hacker_news_query: str
    subtopics: tuple[str, ...]
    used_llm: bool = False


@dataclass
class Candidate:
    title: str
    url: str
    source: str
    format: str
    description: str = ""
    published_at: str = ""
    author: str = ""
    score: float = 0.0
    relevance: float = 0.0
    matched_terms: list[str] = field(default_factory=list)
    subtopic: str = "general"
    explanation: str = ""

