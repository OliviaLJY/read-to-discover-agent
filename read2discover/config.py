from __future__ import annotations

import os
from pathlib import Path


def load_local_env(root: Path | None = None) -> None:
    """Load simple KEY=VALUE files without overwriting existing environment values."""
    root = root or Path.cwd()
    for name in (".env.local", ".env"):
        path = root / name
        if not path.is_file():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip().strip("\"").strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def setting(name: str, default: str = "") -> str:
    load_local_env()
    return os.getenv(name, default)

