from __future__ import annotations

import html

import streamlit as st

from read2discover import DiscoveryPipeline
from read2discover.article_search import fetch_article, search_articles
from read2discover.config import load_local_env, setting
from read2discover.library import ARTICLES, article_text
from read2discover.shelf import article_id, load_shelf, save_article

load_local_env()
st.set_page_config(page_title="Read2Discover Reader", page_icon="◒", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap');
:root { --ink:#172131; --muted:#6f7782; --line:#e5e1d9; --paper:#fbfaf6; --orange:#ef6f45; }
.stApp { background:var(--paper); color:var(--ink); }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
h1,h2,h3 { font-family:'Newsreader',serif !important; color:var(--ink) !important; }
[data-testid="stSidebar"] { background:#f1eee7; border-right:1px solid var(--line); }
[data-testid="stSidebar"] > div { padding-top:1.25rem; }
.brand { font-family:'Newsreader',serif; font-size:1.42rem; font-weight:600; letter-spacing:-.02em; margin-bottom:.1rem; }
.brand-sub { color:var(--muted); font-size:.76rem; margin-bottom:1.5rem; }
.library-label { color:var(--muted); text-transform:uppercase; letter-spacing:.13em; font-size:.68rem; font-weight:700; margin:1.2rem 0 .3rem; }
.search-intro { max-width:760px; margin:0 auto; padding:3rem 1rem 1rem; }
.search-intro h1 { font-size:3.7rem; line-height:.96; margin:.5rem 0 1rem; }
.search-intro p { color:var(--muted); font-family:'Newsreader',serif; font-size:1.25rem; }
.search-card { background:white; border:1px solid var(--line); border-radius:16px; padding:1rem 1.1rem; margin:.75rem 0; }
.search-card .source { color:#8a5db0; font-size:.65rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; }
.search-card h3 { font-size:1.35rem; margin:.3rem 0; }
.search-card p { color:var(--muted); font-size:.82rem; line-height:1.5; margin:0; }
.reader-shell { max-width:760px; margin:0 auto; padding:1.5rem 1.2rem 5rem; }
.section-label { font-size:.72rem; text-transform:uppercase; letter-spacing:.15em; font-weight:700; margin-top:1rem; }
.article-title { font-family:'Newsreader',serif; font-size:clamp(3.1rem,6vw,5.8rem); line-height:.93; letter-spacing:-.045em; margin:1rem 0 1.2rem; color:var(--ink); }
.deck { font-family:'Newsreader',serif; color:#4c5561; font-size:1.48rem; line-height:1.38; margin-bottom:1.7rem; }
.byline { display:flex; align-items:center; gap:.7rem; color:var(--muted); font-size:.82rem; border-bottom:1px solid var(--line); padding-bottom:1.25rem; margin-bottom:2.2rem; }
.avatar { width:30px; height:30px; border-radius:50%; background:var(--ink); color:white; display:inline-flex; align-items:center; justify-content:center; font-size:.7rem; font-weight:700; }
.article-body p { font-family:'Newsreader',serif; font-size:1.26rem; line-height:1.72; color:#27313e; margin:0 0 1.55rem; }
.article-body p:first-child::first-letter { float:left; font-family:'Newsreader',serif; font-size:4rem; line-height:.78; padding:.18rem .45rem 0 0; color:var(--accent); }
.reading-end { display:flex; align-items:center; gap:.7rem; color:var(--muted); font-size:.8rem; margin:2.4rem 0; }
.reading-end:before,.reading-end:after { content:''; height:1px; background:var(--line); flex:1; }
.save-card { background:#f1eee7; border:1px solid var(--line); border-radius:18px; padding:1.15rem 1.2rem; margin:1rem 0 .6rem; }
.save-card .kicker { color:#8a5db0; text-transform:uppercase; letter-spacing:.12em; font-size:.66rem; font-weight:700; }
.save-card h3 { font-size:1.5rem; margin:.35rem 0; }
.save-card p { color:var(--muted); font-size:.82rem; margin:0; }
.discovery-card { position:sticky; top:2rem; background:#172131; color:white; border-radius:22px; padding:1.35rem; margin:6rem 0 1rem; box-shadow:0 18px 50px rgba(23,33,49,.14); }
.discovery-card .kicker { color:#f0a184; text-transform:uppercase; letter-spacing:.13em; font-size:.67rem; font-weight:700; }
.discovery-card h3 { color:white !important; font-family:'Newsreader',serif !important; font-size:1.65rem; line-height:1.08; margin:.55rem 0; }
.discovery-card p { color:#c7ced7; font-size:.83rem; line-height:1.5; margin-bottom:.5rem; }
.source-note { color:#8d96a3; font-size:.7rem; line-height:1.4; margin-top:.7rem; }
.stButton>button { border-radius:999px; background:var(--orange); color:white; border:0; padding:.68rem 1rem; font-weight:700; width:100%; }
.stButton>button:hover { background:#da5d36; color:white; border:0; }
.trail-heading { font-family:'Newsreader',serif; font-size:2.1rem; margin:1.8rem 0 .25rem; }
.trail-summary { color:var(--muted); font-size:.86rem; line-height:1.5; }
.topic-pill { display:inline-block; color:#6a4a3e; background:#f9e8df; padding:.28rem .55rem; border-radius:999px; margin:.25rem .2rem .25rem 0; font-size:.7rem; }
.result { background:white; border:1px solid #e7e2da; border-radius:15px; padding:.85rem .9rem; margin:.65rem 0; box-shadow:0 7px 20px rgba(23,33,49,.04); }
.result:hover { border-color:#e9a58d; transform:translateY(-1px); transition:.15s ease; }
.result-meta { color:#a25338; font-size:.65rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.result-title { font-family:'Newsreader',serif; font-size:1.1rem; font-weight:600; line-height:1.2; margin:.28rem 0; }
.result-title a { color:var(--ink); text-decoration:none; }
.result-why { color:var(--muted); font-size:.74rem; line-height:1.43; }
.mini-stat { color:#7a8490; font-size:.7rem; margin:.7rem 0; }
@media (max-width: 900px) {
  [data-testid="stHorizontalBlock"] { flex-direction:column !important; }
  [data-testid="stColumn"] { width:100% !important; flex:1 1 100% !important; }
  .discovery-card { position:relative; top:auto; margin-top:0; }
  .reader-shell { padding:.8rem .15rem 2rem; }
  .article-title { font-size:2.75rem; line-height:.98; }
  .deck { font-size:1.25rem; }
  .article-body p { font-size:1.15rem; }
  .search-intro { padding:1.5rem .15rem .5rem; }
  .search-intro h1 { font-size:2.35rem; overflow-wrap:anywhere; }
}
</style>
""", unsafe_allow_html=True)

saved_articles = load_shelf()

with st.sidebar:
    st.markdown("<div class='brand'>Read2Discover</div><div class='brand-sub'>A reader with somewhere to go next.</div>", unsafe_allow_html=True)
    search_query = st.text_input("Search articles", placeholder="Search a topic…", key="article_search_query")
    if st.button("Search articles →", key="search_articles"):
        try:
            with st.spinner("Searching articles…"):
                st.session_state["article_search_results"] = search_articles(search_query)
            st.session_state["search_mode"] = True
            st.session_state["show_search_article"] = False
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
    st.markdown("<div class='library-label'>Your reading shelf</div>", unsafe_allow_html=True)
    article_ids = [f"saved:{saved_id}" for saved_id in saved_articles] + list(ARTICLES)
    if st.session_state.pop("pending_clear_library_selection", False):
        st.session_state["library_selection"] = None
    if st.session_state.get("pending_library_selection") in article_ids:
        st.session_state["library_selection"] = st.session_state.pop("pending_library_selection")
    if st.session_state.get("library_selection") not in article_ids:
        st.session_state["library_selection"] = None if st.session_state.get("show_search_article") else article_ids[0]

    def shelf_title(article_id: str) -> str:
        if article_id.startswith("saved:"):
            return saved_articles[article_id.split(":", 1)[1]]["title"]
        return ARTICLES[article_id]["title"]

    selected_id = st.radio(
        "Your reading shelf",
        article_ids,
        format_func=shelf_title,
        label_visibility="collapsed",
        key="library_selection",
        index=None if st.session_state.get("show_search_article") else 0,
    )
    if selected_id is not None and st.session_state.get("_last_library_selection") != selected_id:
        st.session_state["show_search_article"] = False
        st.session_state["search_mode"] = False
        st.session_state["_last_library_selection"] = selected_id
    st.divider()
    st.caption("The article you open becomes the discovery context automatically. No copying or retyping.")
    with st.expander("Add your own reading"):
        custom_title = st.text_input("Title", placeholder="Article or note title")
        custom_body = st.text_area("Text", placeholder="Paste once to add it to the reader…", height=150)
        if st.button("Open in reader", key="open_custom"):
            if len(custom_body.strip()) >= 80:
                custom_article = {
                    "section": "My Reading",
                    "title": custom_title.strip() or "Untitled reading",
                    "deck": "A personal reading added to your shelf.",
                    "author": "You",
                    "date": "Just added",
                    "read_time": f"{max(1, len(custom_body.split()) // 220)} min read",
                    "accent": "#8a5db0",
                    "paragraphs": [p.strip() for p in custom_body.split("\n\n") if p.strip()],
                }
                saved_id = save_article(custom_article)
                st.session_state["show_search_article"] = False
                st.session_state["pending_library_selection"] = f"saved:{saved_id}"
                st.rerun()
            else:
                st.error("Add at least 80 characters.")

if st.session_state.get("search_mode"):
    results = st.session_state.get("article_search_results", [])
    st.markdown(
        f"<div class='search-intro'><div class='section-label' style='color:#8a5db0'>Article search</div><h1>Explore “{html.escape(search_query)}”</h1><p>Choose an article to open it in the reader. It will automatically become the context for your next discovery trail.</p></div>",
        unsafe_allow_html=True,
    )
    search_area = st.container()
    with search_area:
        if not results:
            st.info("No readable articles found. Try a broader topic.")
        for index, item in enumerate(results):
            col_text, col_action = st.columns([4, 1])
            with col_text:
                st.markdown(
                    f"<div class='search-card'><div class='source'>Wikipedia · {item['language'].upper()}</div><h3>{html.escape(item['title'])}</h3><p>{html.escape(item['snippet'])}</p></div>",
                    unsafe_allow_html=True,
                )
            with col_action:
                st.write("")
                st.write("")
                if st.button("Read →", key=f"read_search_{item['language']}_{item['pageid']}"):
                    try:
                        with st.spinner("Opening article…"):
                            st.session_state["search_article"] = fetch_article(item["pageid"], item["language"])
                        st.session_state["show_search_article"] = True
                        st.session_state["search_mode"] = False
                        st.session_state["pending_clear_library_selection"] = True
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
        if st.button("← Back to reading shelf", key="close_search"):
            st.session_state["search_mode"] = False
            st.rerun()
    st.stop()

if st.session_state.get("show_search_article"):
    article = st.session_state.get("search_article")
elif selected_id and selected_id.startswith("saved:"):
    article = saved_articles[selected_id.split(":", 1)[1]]
else:
    article = ARTICLES[selected_id or next(iter(ARTICLES))]
if article is None:
    article = ARTICLES[next(iter(ARTICLES))]
if article is st.session_state.get("search_article"):
    article_key = f"search_{article.get('title', 'article')}"
else:
    article_key = selected_id or next(iter(ARTICLES))
reading = article_text(article)

reader_col, discover_col = st.columns([1.72, .78], gap="large")

with reader_col:
    initials = "".join(part[0] for part in article["author"].split()[:2]).upper()
    paragraphs = "".join(f"<p>{html.escape(p)}</p>" for p in article["paragraphs"])
    st.markdown(
        f"""<div class='reader-shell' style='--accent:{article['accent']}'>
        <div class='section-label' style='color:{article['accent']}'>{html.escape(article['section'])}</div>
        <div class='article-title'>{html.escape(article['title'])}</div>
        <div class='deck'>{html.escape(article['deck'])}</div>
        <div class='byline'><span class='avatar'>{initials}</span><span>By <b>{html.escape(article['author'])}</b></span><span>·</span><span>{html.escape(article['date'])}</span><span>·</span><span>{html.escape(article['read_time'])}</span></div>
        <div class='article-body'>{paragraphs}</div><div class='reading-end'>End of article</div></div>""",
        unsafe_allow_html=True,
    )
    if article.get("source_url"):
        st.caption(f"Source: {article['source_url']}")
    saved_id = article_id(article)
    already_saved = saved_id in saved_articles or selected_id in ARTICLES
    st.markdown(
        """<div class='save-card'><div class='kicker'>Your reading shelf</div><h3>Keep this reading</h3>
        <p>Save it here so you can return later and continue exploring from the same article.</p></div>""",
        unsafe_allow_html=True,
    )
    if already_saved:
        st.button("✓ Saved to your shelf", disabled=True, key=f"saved_{article_key}")
    elif st.button("＋ Save to my shelf", key=f"save_{article_key}"):
        saved_id = save_article(article)
        st.session_state["show_search_article"] = False
        st.session_state["pending_library_selection"] = f"saved:{saved_id}"
        st.success("Saved to your shelf.")
        st.rerun()

with discover_col:
    st.markdown(
        """<div class="discovery-card"><div class="kicker">Follow the thread</div><h3>Keep exploring this idea</h3>
        <p>One click turns the article you are reading into a balanced trail of videos and discussions.</p></div>""",
        unsafe_allow_html=True,
    )
    discover = st.button("Discover from this reading →", key=f"discover_{article_key}")
    st.markdown("<div class='source-note'>YouTube + Hacker News · 5 recommendations · one retry maximum</div>", unsafe_allow_html=True)

    result_key = f"result_{article_key}"
    if discover:
        try:
            with st.spinner("Following the ideas in this article…"):
                st.session_state[result_key] = DiscoveryPipeline(use_llm=bool(setting("PARLEY_API_KEY"))).discover(reading)
        except Exception as exc:
            st.error(str(exc))

    result = st.session_state.get(result_key)
    if result:
        st.markdown("<div class='trail-heading'>Your next trail</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='trail-summary'>{html.escape(result.plan.summary)}</div>", unsafe_allow_html=True)
        st.markdown("".join(f"<span class='topic-pill'>{html.escape(topic)}</span>" for topic in result.plan.topics), unsafe_allow_html=True)
        st.markdown(
            f"<div class='mini-stat'>{result.source_counts.get('YouTube', 0)} video candidates · {result.source_counts.get('Hacker News', 0)} Hacker News candidates · {'retried once' if result.retry_used else 'first search worked'}</div>",
            unsafe_allow_html=True,
        )
        for i, item in enumerate(result.recommendations, 1):
            st.markdown(
                f"""<div class="result"><div class="result-meta">{i:02d} · {html.escape(item.source)} · {html.escape(item.format)}</div>
                <div class="result-title"><a href="{html.escape(item.url)}" target="_blank">{html.escape(item.title)}</a></div>
                <div class="result-why">{html.escape(item.explanation)}</div></div>""",
                unsafe_allow_html=True,
            )
        for warning in result.warnings:
            st.caption(warning)
        with st.expander("How this trail was made"):
            st.json({
                "topics": result.plan.topics,
                "youtube_query": result.plan.youtube_query,
                "hacker_news_query": result.plan.hacker_news_query,
                "subtopics": result.plan.subtopics,
                "retry_used": result.retry_used,
            })
