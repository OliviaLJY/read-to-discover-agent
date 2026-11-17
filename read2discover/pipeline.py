from __future__ import annotations

from dataclasses import dataclass, field

from .agent import plan_interests
from .models import Candidate, InterestPlan
from .ranking import rank
from .retrievers import search_hacker_news, search_youtube


@dataclass
class PipelineResult:
    plan: InterestPlan
    recommendations: list[Candidate]
    source_counts: dict[str, int]
    retry_used: bool = False
    youtube_demo: bool = False
    warnings: list[str] = field(default_factory=list)


class DiscoveryPipeline:
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm

    def discover(self, reading: str) -> PipelineResult:
        if len(reading.strip()) < 80:
            raise ValueError("Paste at least 80 characters so the agent has enough context.")
        plan = plan_interests(reading, self.use_llm)
        warnings: list[str] = []
        retry_used = False
        try:
            hn = search_hacker_news(plan.hacker_news_query)
        except Exception as exc:
            hn = []
            warnings.append(f"Hacker News retrieval failed: {type(exc).__name__}")
        try:
            youtube, demo = search_youtube(plan.youtube_query)
        except Exception as exc:
            youtube, demo = [], False
            warnings.append(f"YouTube retrieval failed: {type(exc).__name__}")

        # A source can technically succeed yet return too little variety for a
        # credible Top-5. Use the single allowed retry when either required
        # source yields fewer than five candidates.
        if len(hn) < 5 or len(youtube) < 5:
            retry_used = True
            if len(hn) < 5:
                try:
                    hn = search_hacker_news(plan.topics[0])
                except Exception:
                    pass
            if len(youtube) < 5:
                try:
                    youtube, demo = search_youtube(plan.topics[0])
                except Exception:
                    pass

        recommendations = rank(hn + youtube, plan, 5)
        counts = {"Hacker News": len(hn), "YouTube": len(youtube)}
        if demo:
            warnings.append("YouTube is using the deterministic demo catalog. Add YOUTUBE_API_KEY for live results.")
        if not plan.used_llm:
            warnings.append("Keyword planning fallback was used because the LLM was disabled or unavailable.")
        return PipelineResult(plan, recommendations, counts, retry_used, demo, warnings)

