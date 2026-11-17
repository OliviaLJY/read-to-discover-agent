# Read2Discover

Read2Discover is a reading website with discovery built into the reading flow. A reader can search for an English or Chinese topic, open a full Wikipedia article inside the reader, choose an article from the shelf, or add personal text. At the end of a searched article, a single button saves it to a persistent local shelf. One click continues the idea - the open article automatically becomes the context for an explained feed from YouTube and Hacker News. No retyping or copying is required.

The MVP follows a deliberately bounded loop: extract interests from the open article, plan one query per required source, retrieve candidates, rank for relevance and diversity, and allow at most one retry when a source underperforms.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Configuration is read from `.env.local`, `.env`, or the process environment:

- `PARLEY_API_KEY` - MIT Parley key for LLM interest extraction and explanations.
- `PARLEY_BASE_URL` - optional; defaults to `https://parley.api.mit.edu/v1`.
- `PARLEY_MODEL` - optional; defaults to `gpt-5-mini`.
- `YOUTUBE_API_KEY` - Google YouTube Data API v3 key. Without it, the UI uses a clearly marked deterministic demo catalog so the two-source loop remains testable.

The Hacker News search uses the public Algolia HN Search API. No key is needed.

## Test and evaluate

```bash
python3 -m unittest discover -s tests -v
python3 scripts/evaluate.py
```

The evaluation set is held out from ranking logic. Labels are defined before tuning:

- `relevant`: item directly addresses a named topic, entity, or inferred interest in the reading.
- `subtopic`: the single primary angle covered by the item; diversity is the count of distinct relevant subtopics in the Top 5.
- `format`: `video`, `article`, or `discussion`; the product target is at least two formats.

The report compares the agent ranking against a keyword-overlap baseline and reports completion, relevance@5, subtopic diversity, format diversity, and source coverage.

## Scope

Included: bilingual article search, Wikipedia article import, an article shelf and reader, persistent local shelf saving with duplicate prevention, optional personal reading import, Parley-assisted planning with deterministic fallback, YouTube + Hacker News retrieval, URL validation, deduplication, relevance/diversity ranking, explanations, and one bounded retry.

Deferred: Bluesky and learning from user feedback. These should stay optional until the required two-source loop is reliable.

