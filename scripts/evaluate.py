from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from read2discover.agent import keyword_plan
from read2discover.models import Candidate
from read2discover.ranking import keyword_baseline, rank


def candidates(scenario: dict) -> list[Candidate]:
    terms = scenario["relevant_terms"]
    subs = scenario["subtopics"]
    return [
        Candidate(f"{terms[0].title()} and {subs[0]} explained", f"https://youtube.com/watch?v={scenario['id']}1", "YouTube", "video", terms[1]),
        Candidate(f"A field guide to {terms[2]}", f"https://example.com/{scenario['id']}/guide", "Hacker News", "article", f"{terms[3]} {subs[1]}"),
        Candidate(f"Debating {terms[4]} and {subs[2]}", f"https://news.ycombinator.com/item?id={len(scenario['id'])}", "Hacker News", "discussion", terms[5]),
        Candidate("Unrelated celebrity roundup", f"https://example.org/{scenario['id']}/noise", "Hacker News", "article", "entertainment gossip"),
        Candidate(f"New perspectives on {terms[1]}", f"https://youtube.com/watch?v={scenario['id']}2", "YouTube", "video", subs[1]),
        Candidate(f"{terms[5].title()} case study", f"https://example.net/{scenario['id']}/case", "Hacker News", "article", subs[2]),
    ]


def metrics(feed: list[Candidate], scenario: dict) -> dict:
    labels = {term.lower() for term in scenario["relevant_terms"]}
    relevant = []
    found_subtopics = set()
    for item in feed:
        text = f"{item.title} {item.description}".lower()
        if any(term in text for term in labels):
            relevant.append(item)
            found_subtopics.update(sub for sub in scenario["subtopics"] if sub.lower() in text)
    return {
        "completion": len(feed) == 5,
        "relevance_at_5": round(len(relevant) / max(1, len(feed)), 2),
        "subtopic_diversity": len(found_subtopics),
        "format_diversity": len({item.format for item in feed}),
        "source_coverage": len({item.source for item in feed}),
    }


def main() -> None:
    scenarios = json.loads(Path("evals/scenarios.json").read_text())
    report = []
    for scenario in scenarios:
        plan = keyword_plan(scenario["reading"])
        agent = rank(deepcopy(candidates(scenario)), plan, 5)
        base = keyword_baseline(deepcopy(candidates(scenario)), scenario["reading"], 5)
        for item in base:
            item.subtopic = max(scenario["subtopics"], key=lambda s: int(s.lower() in (item.title + " " + item.description).lower()))
        report.append({"scenario": scenario["id"], "agent": metrics(agent, scenario), "baseline": metrics(base, scenario)})
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
