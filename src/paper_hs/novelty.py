from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .metadata import WorkMetadata, search_arxiv, search_crossref, search_openalex, search_semantic_scholar, similarity
from .paths import paper_hs_dir

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "with", "by", "as", "is", "are",
    "we", "our", "this", "that", "from", "using", "use", "method", "paper", "approach", "model",
}

RISKY_PHRASES = [
    "first", "novel", "new", "state-of-the-art", "sota", "outperforms", "solves", "generalizes",
    "no prior work", "comprehensive", "unified", "unprecedented",
]


def load_idea(project: str | Path, query: str | None = None) -> str:
    if query:
        return query.strip()
    path = paper_hs_dir(project) / "idea.md"
    if path.exists():
        text = path.read_text(encoding="utf-8", errors="ignore")
        text = re.sub(r"^#.*$", "", text, flags=re.M).strip()
        if text:
            return text
    claim_path = paper_hs_dir(project) / "state" / "claim_graph.json"
    if claim_path.exists():
        try:
            data = json.loads(claim_path.read_text(encoding="utf-8"))
            claims = data.get("claims", [])
            texts = [c.get("text", "") for c in claims if isinstance(c, dict)]
            if texts:
                return " ".join(texts[:3])
        except Exception:
            pass
    return ""


def keywords(text: str, n: int = 18) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower())
    counts: dict[str, int] = {}
    for w in words:
        if w in STOPWORDS:
            continue
        counts[w] = counts.get(w, 0) + 1
    return [w for w, _ in sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:n]]


def _risk_from_scores(scores: list[float]) -> str:
    if not scores:
        return "unknown"
    top = max(scores)
    count_close = sum(1 for s in scores if s >= 0.58)
    if top >= 0.74 or count_close >= 3:
        return "high"
    if top >= 0.55 or count_close >= 1:
        return "medium"
    return "low"


def novelty_landscape(project: str | Path, query: str | None = None, online: bool = False, rows: int = 10, mailto: str | None = None) -> dict[str, Any]:
    idea = load_idea(project, query)
    if not idea:
        return {
            "query": "",
            "risk_level": "unknown",
            "nearest_works": [],
            "risky_phrases": [],
            "safe_phrasing": [],
            "limitations": ["No idea statement or claim graph text was available."],
        }

    terms = keywords(idea)
    search_query = " ".join(terms[:12]) or idea[:240]
    works: list[WorkMetadata] = []
    limitations: list[str] = []
    if online:
        try:
            works.extend(search_openalex(search_query, rows=rows, mailto=mailto))
        except Exception as exc:
            limitations.append(f"OpenAlex search failed: {exc}")
        try:
            works.extend(search_crossref(search_query, rows=rows, mailto=mailto))
        except Exception as exc:
            limitations.append(f"Crossref search failed: {exc}")
        try:
            works.extend(search_semantic_scholar(search_query, rows=rows))
        except Exception as exc:
            limitations.append(f"Semantic Scholar search failed: {exc}")
        try:
            works.extend(search_arxiv(search_query, rows=rows))
        except Exception as exc:
            limitations.append(f"arXiv search failed: {exc}")
    else:
        limitations.append("Online search was not run. Novelty risk is based only on wording checks.")

    dedup: dict[str, WorkMetadata] = {}
    for w in works:
        key = (w.doi or w.title).lower()
        if key and key not in dedup:
            dedup[key] = w
    scored = []
    for w in dedup.values():
        text = " ".join([w.title or "", w.abstract or ""])
        score = similarity(idea, text)
        scored.append({**w.as_dict(), "similarity": round(score, 3)})
    scored.sort(key=lambda x: x["similarity"], reverse=True)
    scores = [x["similarity"] for x in scored]
    risky = [p for p in RISKY_PHRASES if re.search(r"\b" + re.escape(p) + r"\b", idea, flags=re.I)]
    risk_level = _risk_from_scores(scores)
    if risky and risk_level == "low":
        risk_level = "medium"
    if not online:
        risk_level = "unknown"

    safe = [
        "State the contribution as a bounded combination of mechanism, setting, and evidence.",
        "Use 'to our knowledge' only after logging the prior-art search and verifying close works.",
        "Replace broad novelty claims with precise differentiators against the nearest works.",
    ]
    return {
        "query": idea,
        "search_query": search_query,
        "keywords": terms,
        "risk_level": risk_level,
        "nearest_works": scored[:rows],
        "risky_phrases": risky,
        "safe_phrasing": safe,
        "limitations": limitations + ["Metadata search is a prior-art risk map, not proof of novelty or publishability."],
    }


def novelty_report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Novelty and prior-art landscape report",
        "",
        f"Risk level: **{report.get('risk_level', 'unknown')}**",
        "",
        "## Query",
        "",
        report.get("query", "") or "No query provided.",
        "",
        "## Search query",
        "",
        report.get("search_query", ""),
        "",
        "## Nearest works",
        "",
    ]
    works = report.get("nearest_works") or []
    if not works:
        lines.append("No works retrieved. Run with `--online` or provide a sharper idea statement.")
    else:
        for i, w in enumerate(works, 1):
            authors = ", ".join((w.get("authors") or [])[:3])
            lines.append(f"{i}. **{w.get('title','')}** ({w.get('year','')}) — similarity `{w.get('similarity')}`")
            if authors:
                lines.append(f"   - Authors: {authors}")
            if w.get("venue"):
                lines.append(f"   - Venue/source: {w.get('venue')}")
            if w.get("doi"):
                lines.append(f"   - DOI: {w.get('doi')}")
    lines.extend([
        "",
        "## Risky phrases detected",
        "",
    ])
    risky = report.get("risky_phrases") or []
    lines.append(", ".join(risky) if risky else "No risky novelty phrases detected in the idea statement.")
    lines.extend([
        "",
        "## Safer phrasing guidance",
        "",
    ])
    for s in report.get("safe_phrasing") or []:
        lines.append(f"- {s}")
    lines.extend([
        "",
        "## Limitations",
        "",
    ])
    for l in report.get("limitations") or []:
        lines.append(f"- {l}")
    return "\n".join(lines) + "\n"
