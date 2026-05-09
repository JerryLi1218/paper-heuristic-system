from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .bibtex import BibEntry, parse_bibtex_files
from .citation_audit import _entry_arxiv, _load_jsonl
from .latex import discover_bib_files, extract_citation_keys
from .paths import state_dir
from .project import iter_files


def _next_source_id(existing: set[str], idx: int) -> str:
    while True:
        sid = f"S{idx:04d}"
        if sid not in existing:
            return sid
        idx += 1


def _canonical_id(entry: BibEntry) -> str:
    arxiv = _entry_arxiv(entry)
    if entry.doi:
        return f"doi:{entry.doi}"
    if arxiv:
        return f"arxiv:{arxiv}"
    return f"bib:{entry.key}"


def card_from_entry(entry: BibEntry, source_id: str, cited: bool) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "bib_key": entry.key,
        "canonical_id": _canonical_id(entry),
        "doi": entry.doi,
        "arxiv": _entry_arxiv(entry),
        "title": entry.title,
        "authors": entry.authors,
        "year": entry.year,
        "usage": "" if not cited else "cited in manuscript; fill intended use before relying on this source",
        "supports_claims": [],
        "verification_status": "unverified",
        "notes": "Generated from local BibTeX. Verify title/year/authors/DOI and fill usage/support before making novelty-sensitive claims.",
    }


def generate_source_cards(project: str | Path, overwrite: bool = False, cited_only: bool = False) -> dict[str, Any]:
    root = Path(project).expanduser().resolve()
    manuscript = root / "manuscript"
    base = manuscript if manuscript.exists() else root
    tex_files = iter_files(base, [".tex"])
    bib_files = iter_files(base, [".bib"])
    bib_files = sorted(set(bib_files) | discover_bib_files(tex_files, root))
    cited_keys = extract_citation_keys(tex_files)
    entries, duplicate_keys = parse_bibtex_files(bib_files)
    by_key = {e.key: e for e in entries}

    out_path = state_dir(root) / "source_cards.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    existing_cards, existing_issues = _load_jsonl(out_path)
    existing_by_key = {str(c.get("bib_key") or ""): c for c in existing_cards if c.get("bib_key")}
    used_ids = {str(c.get("source_id") or "") for c in existing_cards if c.get("source_id")}

    generated: list[dict[str, Any]] = []
    next_idx = 1
    for entry in entries:
        if cited_only and entry.key not in cited_keys:
            continue
        if entry.key in existing_by_key and not overwrite:
            generated.append(existing_by_key[entry.key])
            continue
        sid = _next_source_id(used_ids, next_idx)
        used_ids.add(sid)
        try:
            next_idx = int(sid[1:]) + 1
        except ValueError:
            next_idx += 1
        generated.append(card_from_entry(entry, sid, cited=entry.key in cited_keys))

    # Preserve existing cards whose bib_key is not in current BibTeX unless overwrite is requested.
    if not overwrite:
        generated_keys = {str(c.get("bib_key") or "") for c in generated}
        for card in existing_cards:
            if str(card.get("bib_key") or "") not in generated_keys:
                generated.append(card)

    out_path.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in generated), encoding="utf-8")
    missing_cited = sorted(k for k in cited_keys if k not in by_key)
    return {
        "project": str(root),
        "output": str(out_path),
        "tex_files": len(tex_files),
        "bib_files": len(bib_files),
        "bib_entries": len(entries),
        "cited_keys": len(cited_keys),
        "source_cards": len(generated),
        "duplicate_bib_keys": duplicate_keys,
        "missing_cited_keys": missing_cited,
        "parse_issues": [i.__dict__ for i in existing_issues],
        "overwrite": overwrite,
        "cited_only": cited_only,
    }


def source_cards_report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Source-card generation report",
        "",
        f"Project: `{report['project']}`",
        f"Output: `{report['output']}`",
        "",
        "## Summary",
        "",
        f"- TeX files: {report['tex_files']}",
        f"- BibTeX files: {report['bib_files']}",
        f"- BibTeX entries: {report['bib_entries']}",
        f"- Cited keys: {report['cited_keys']}",
        f"- Source cards written: {report['source_cards']}",
        f"- Overwrite: {report['overwrite']}",
        f"- Cited only: {report['cited_only']}",
        "",
        "## Follow-up",
        "",
        "Generated source cards are conservative placeholders. Fill `usage`, `supports_claims`, and verification notes before relying on a source for novelty, SOTA, first-to-do, or submission-readiness claims.",
    ]
    if report.get("duplicate_bib_keys"):
        lines.extend(["", "## Duplicate BibTeX keys", ""])
        for k in report["duplicate_bib_keys"]:
            lines.append(f"- `{k}`")
    if report.get("missing_cited_keys"):
        lines.extend(["", "## Cited keys missing from BibTeX", ""])
        for k in report["missing_cited_keys"]:
            lines.append(f"- `{k}`")
    return "\n".join(lines) + "\n"
