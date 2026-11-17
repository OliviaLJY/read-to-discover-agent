from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


DEFAULT_SHELF_PATH = Path.cwd() / "data" / "shelf.json"


def article_id(article: dict) -> str:
    identity = str(article.get("source_url") or article.get("title") or "untitled").strip().lower()
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]


def load_shelf(path: Path | None = None) -> dict[str, dict]:
    target = path or DEFAULT_SHELF_PATH
    if not target.is_file():
        return {}
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(key): value for key, value in data.items() if isinstance(value, dict)}


def save_article(article: dict, path: Path | None = None) -> str:
    target = path or DEFAULT_SHELF_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    saved = load_shelf(target)
    saved_id = article_id(article)
    saved[saved_id] = article
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(saved, ensure_ascii=False, indent=2), encoding="utf-8")
    os.chmod(temporary, 0o600)
    temporary.replace(target)
    return saved_id

