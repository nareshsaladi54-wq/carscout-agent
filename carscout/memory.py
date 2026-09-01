"""A memory you can read. Notes appended to Markdown, one line per fact,
namespaced by buyer. Backed by AgentCore Memory in a deployment."""
from __future__ import annotations

import datetime
import pathlib

from .config import DATA_DIR

MEM_FILE = pathlib.Path(DATA_DIR) / "memory.md"


def remember(actor_id: str, note: str) -> str:
    MEM_FILE.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.date.today().isoformat()
    with open(MEM_FILE, "a") as fh:
        fh.write(f"- [{stamp}] ({actor_id}) {note.strip()}\n")
    return "noted"


def recall(actor_id: str, query: str = "") -> list[str]:
    if not MEM_FILE.exists():
        return []
    lines = [ln.strip() for ln in MEM_FILE.read_text().splitlines() if ln.strip()]
    hits = [ln for ln in lines if f"({actor_id})" in ln]
    if query:
        terms = [t for t in query.lower().split() if len(t) > 2]
        hits = [ln for ln in hits if any(t in ln.lower() for t in terms)] or hits
    return hits[-12:]
