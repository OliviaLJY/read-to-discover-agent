import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from read2discover.agent import keyword_plan
from read2discover.article_search import _language_for, _plain_snippet, estimate_read_time
from read2discover.models import Candidate, InterestPlan
from read2discover.pipeline import DiscoveryPipeline
from read2discover.ranking import deduplicate, rank
from read2discover.shelf import article_id, load_shelf, save_article
from read2discover.text import overlap


READING = "Retrieval augmented generation grounds language models in evidence. Evaluation datasets measure factuality, provenance, and uncertainty in research assistants."


class CoreTests(unittest.TestCase):
    def test_saved_reading_persists_and_deduplicates(self):
        article = {"title": "A saved reading", "source_url": "https://example.com/read", "paragraphs": ["Body"]}
        with TemporaryDirectory() as directory:
            path = Path(directory) / "shelf.json"
            first_id = save_article(article, path)
            second_id = save_article(article, path)
            saved = load_shelf(path)
        self.assertEqual(first_id, article_id(article))
        self.assertEqual(first_id, second_id)
        self.assertEqual(list(saved), [first_id])
        self.assertEqual(saved[first_id]["title"], "A saved reading")

    def test_article_search_detects_language_and_cleans_snippets(self):
        self.assertEqual(_language_for("urban heat"), "en")
        self.assertEqual(_language_for("城市热岛"), "zh")
        self.assertEqual(_plain_snippet("An <span>urban</span> &amp; climate topic"), "An urban & climate topic")

    def test_read_time_uses_only_displayed_content(self):
        english = ["word " * 220, "word " * 220]
        chinese = ["热" * 400, "岛" * 400]
        self.assertEqual(estimate_read_time(english, "en"), "2 min read")
        self.assertEqual(estimate_read_time(chinese, "zh"), "约 2 分钟")

    def test_keyword_plan_has_source_specific_queries(self):
        plan = keyword_plan(READING)
        self.assertGreaterEqual(len(plan.topics), 3)
        self.assertIn("explained", plan.youtube_query)
        self.assertTrue(plan.hacker_news_query)

    def test_deduplication_and_invalid_urls(self):
        items = [
            Candidate("Same title", "https://example.com/a", "HN", "article"),
            Candidate("Same title", "https://other.com/b", "YouTube", "video"),
            Candidate("Broken", "javascript:alert(1)", "HN", "article"),
        ]
        self.assertEqual(len(deduplicate(items)), 1)

    def test_common_words_do_not_create_false_relevance(self):
        score, matches = overlap(
            "A cooking video for beginners and families",
            ["evaluation frameworks and metrics for factuality"],
        )
        self.assertEqual(score, 0)
        self.assertEqual(matches, [])

    def test_rank_balances_sources_and_formats(self):
        plan = InterestPlan("", ("retrieval", "factuality"), "", "", ("evaluation", "provenance"))
        items = [
            Candidate("Retrieval and factuality", "https://a.com/1", "Hacker News", "article", "evaluation"),
            Candidate("Retrieval explained", "https://youtube.com/watch?v=1", "YouTube", "video", "provenance"),
            Candidate("Factuality benchmarks", "https://b.com/2", "Hacker News", "article", "evaluation"),
        ]
        feed = rank(items, plan, 3)
        self.assertEqual({x.format for x in feed}, {"article", "video"})
        self.assertEqual({x.source for x in feed}, {"Hacker News", "YouTube"})

    def test_top_five_reserves_two_slots_per_required_source(self):
        plan = InterestPlan("", ("retrieval", "factuality"), "", "", ("evaluation", "provenance"))
        items = [
            Candidate(f"Retrieval video {i}", f"https://youtube.com/watch?v={i}", "YouTube", "video", "factuality")
            for i in range(5)
        ] + [
            Candidate(f"Retrieval article {i}", f"https://example.com/{i}", "Hacker News", "article", "factuality")
            for i in range(3)
        ]
        feed = rank(items, plan, 5)
        counts = {source: sum(item.source == source for item in feed) for source in {"YouTube", "Hacker News"}}
        self.assertGreaterEqual(counts["YouTube"], 2)
        self.assertGreaterEqual(counts["Hacker News"], 2)

    @patch("read2discover.pipeline.search_youtube")
    @patch("read2discover.pipeline.search_hacker_news")
    @patch("read2discover.pipeline.plan_interests")
    def test_pipeline_uses_at_most_one_retry(self, mock_plan, mock_hn, mock_yt):
        mock_plan.return_value = InterestPlan("", ("ai", "safety"), "ai safety", "ai safety", ("evals", "policy"))
        mock_hn.side_effect = [[], [Candidate("AI safety evals", "https://news.ycombinator.com/item?id=1", "Hacker News", "article")]]
        mock_yt.side_effect = [([], False), ([Candidate("AI safety policy", "https://youtube.com/watch?v=1", "YouTube", "video")], False)]
        result = DiscoveryPipeline(False).discover(READING)
        self.assertTrue(result.retry_used)
        self.assertEqual(mock_hn.call_count, 2)
        self.assertEqual(mock_yt.call_count, 2)


if __name__ == "__main__":
    unittest.main()

