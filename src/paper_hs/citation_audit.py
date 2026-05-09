from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json
import re

from .bibtex import BibEntry, is_plausible_doi, normalize_doi, parse_bibtex_files
from .latex import discover_bib_files, extract_citation_keys
from .metadata import crossref_by_doi, openalex_by_doi, similarity
from .project import iter_files


@dataclass
class CitationIssue:
    severity: str
    code: str
    message: str
    key: str | None = None
    details: dict[str, Any] | None = None


def _first_author_last(authors: list[str]) -> str:
    if not authors:
        return ""
    first = authors[0].strip()
    if ',' in first:
        return first.split(',', 1)[0].strip().lower()
    return first.split()[-1].lower() if first.split() else ""


def _norm_text(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9 ]+", " ", value or "").lower()
    return re.sub(r"\s+", " ", value).strip()


def _norm_year(value: Any) -> str:
    m = re.search(r"\d{4}", str(value or ""))
    return m.group(0) if m else ""


def _norm_arxiv(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"^arxiv:", "", value)
    value = re.sub(r"^https?://arxiv\.org/(abs|pdf)/", "", value)
    value = value.replace(".pdf", "")
    return value


def _load_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[CitationIssue]]:
    rows: list[dict[str, Any]] = []
    issues: list[CitationIssue] = []
    if not path.exists():
        return rows, issues
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            if isinstance(row, dict):
                rows.append(row)
            else:
                issues.append(CitationIssue("error", "source_card_not_object", "Source-card JSONL row is not an object.", None, {"line": i}))
        except json.JSONDecodeError as exc:
            issues.append(CitationIssue("error", "source_card_json_error", f"Source-card JSON parse error: {exc}", None, {"line": i}))
    return rows, issues


def _entry_arxiv(entry: BibEntry) -> str:
    return _norm_arxiv(entry.fields.get("arxiv", "") or entry.fields.get("eprint", ""))


def _source_card_id(card: dict[str, Any]) -> str:
    return str(card.get("source_id") or card.get("id") or "")


def _verify_source_cards(
    root: Path,
    cited_keys: set[str],
    by_key: dict[str, BibEntry],
) -> tuple[list[dict[str, Any]], list[CitationIssue]]:
    """Verify source_cards.jsonl against local BibTeX entries.

    This is the check that catches the common agent failure where the agent located
    the correct source path or source_id but emitted a different or malformed bib_key.
    """
    path = root / "paper_hs" / "state" / "source_cards.jsonl"
    cards, issues = _load_jsonl(path)
    if not path.exists():
        issues.append(CitationIssue("warning", "source_cards_missing", "paper_hs/state/source_cards.jsonl is missing; citation support cannot be audited against source cards."))
        return cards, issues

    by_source_id: dict[str, dict[str, Any]] = {}
    by_bib_key: dict[str, list[dict[str, Any]]] = {}
    for card in cards:
        sid = _source_card_id(card)
        bib_key = str(card.get("bib_key") or "")
        if not sid:
            issues.append(CitationIssue("warning", "source_card_missing_source_id", "A source card has no source_id.", bib_key or None))
        elif sid in by_source_id:
            issues.append(CitationIssue("error", "duplicate_source_id", "Duplicate source_id in source_cards.jsonl.", bib_key or None, {"source_id": sid}))
        else:
            by_source_id[sid] = card
        if not bib_key:
            issues.append(CitationIssue("warning", "source_card_missing_bib_key", "A source card has no bib_key.", sid or None))
            continue
        by_bib_key.setdefault(bib_key, []).append(card)
        if bib_key not in by_key:
            issues.append(CitationIssue("error", "source_card_bib_key_missing", "Source card points to a bib_key that does not exist in local .bib files.", bib_key, {"source_id": sid}))

    for key in sorted(cited_keys):
        if key not in by_bib_key:
            issues.append(CitationIssue("warning", "cited_key_without_source_card", "Cited key has no source card, so claim-support and novelty use cannot be audited.", key))

    for bib_key, matches in sorted(by_bib_key.items()):
        if len(matches) > 1:
            issues.append(CitationIssue("warning", "multiple_source_cards_same_bib_key", "Multiple source cards map to the same bib_key.", bib_key, {"source_ids": [_source_card_id(c) for c in matches]}))
        entry = by_key.get(bib_key)
        if not entry:
            continue
        for card in matches:
            sid = _source_card_id(card)
            card_title = str(card.get("title") or card.get("canonical_title") or "")
            if card_title and entry.title:
                score = similarity(_norm_text(card_title), _norm_text(entry.title))
                if score < 0.75:
                    issues.append(CitationIssue("error", "source_card_title_mismatch", "Source-card title does not match the local BibTeX title. This often means the agent found one paper but wrote another bib entry/key.", bib_key, {"source_id": sid, "source_title": card_title, "bib_title": entry.title, "similarity": round(score, 3)}))
            card_year = _norm_year(card.get("year"))
            if card_year and entry.year and card_year != entry.year:
                issues.append(CitationIssue("warning", "source_card_year_mismatch", "Source-card year differs from local BibTeX year.", bib_key, {"source_id": sid, "source_year": card_year, "bib_year": entry.year}))
            card_doi = normalize_doi(str(card.get("doi") or ""))
            if card_doi and entry.doi and card_doi != entry.doi:
                issues.append(CitationIssue("error", "source_card_doi_mismatch", "Source-card DOI differs from local BibTeX DOI.", bib_key, {"source_id": sid, "source_doi": card_doi, "bib_doi": entry.doi}))
            card_arxiv = _norm_arxiv(str(card.get("arxiv") or card.get("arxiv_id") or ""))
            bib_arxiv = _entry_arxiv(entry)
            if card_arxiv and bib_arxiv and card_arxiv != bib_arxiv:
                issues.append(CitationIssue("error", "source_card_arxiv_mismatch", "Source-card arXiv/eprint ID differs from local BibTeX arXiv/eprint ID.", bib_key, {"source_id": sid, "source_arxiv": card_arxiv, "bib_arxiv": bib_arxiv}))
            usage = card.get("usage") or card.get("used_for") or card.get("supports_text")
            if bib_key in cited_keys and not usage:
                issues.append(CitationIssue("warning", "source_card_missing_usage", "Cited source card does not explain why this source is being used.", bib_key, {"source_id": sid}))
            status = str(card.get("verification_status") or "").lower()
            if bib_key in cited_keys and status in {"", "unverified"}:
                issues.append(CitationIssue("warning", "source_card_unverified", "Cited source card is unverified; check metadata/content before relying on it.", bib_key, {"source_id": sid}))

    # Optional citation_claims ledger: catches source_id -> bib_key drift.
    claims_path = root / "paper_hs" / "state" / "citation_claims.jsonl"
    claim_rows, claim_issues = _load_jsonl(claims_path)
    issues.extend([CitationIssue(i.severity, "citation_claim_" + i.code, i.message, i.key, i.details) for i in claim_issues])
    for row in claim_rows:
        sid = str(row.get("source_id") or "")
        bib_key = str(row.get("bib_key") or "")
        claim_id = str(row.get("claim_id") or "")
        if sid and sid not in by_source_id:
            issues.append(CitationIssue("error", "citation_claim_missing_source", "citation_claims.jsonl references a missing source_id.", bib_key or None, {"source_id": sid, "claim_id": claim_id}))
        if bib_key and bib_key not in by_key:
            issues.append(CitationIssue("error", "citation_claim_missing_bib_key", "citation_claims.jsonl references a missing local bib_key.", bib_key, {"source_id": sid, "claim_id": claim_id}))
        if sid and bib_key and sid in by_source_id:
            expected = str(by_source_id[sid].get("bib_key") or "")
            if expected and expected != bib_key:
                issues.append(CitationIssue("error", "citation_claim_bib_source_mismatch", "citation_claims.jsonl bib_key disagrees with the source card for the same source_id.", bib_key, {"source_id": sid, "expected_bib_key": expected, "claim_id": claim_id}))

    return cards, issues


def _verify_entry_online(entry: BibEntry, mailto: str | None = None) -> tuple[dict[str, Any] | None, list[CitationIssue]]:
    issues: list[CitationIssue] = []
    if not entry.doi:
        return None, issues
    meta = None
    try:
        meta = crossref_by_doi(entry.doi, mailto=mailto)
    except Exception as exc:
        issues.append(CitationIssue("info", "crossref_lookup_failed", f"Crossref lookup failed: {exc}", entry.key))
    if meta is None:
        try:
            meta = openalex_by_doi(entry.doi, mailto=mailto)
        except Exception as exc:
            issues.append(CitationIssue("warning", "metadata_lookup_failed", f"OpenAlex lookup failed: {exc}", entry.key))
    if not meta:
        return None, issues

    md = meta.as_dict()
    title_score = similarity(entry.title, meta.title)
    if entry.title and meta.title and title_score < 0.72:
        issues.append(CitationIssue(
            "error", "doi_title_mismatch",
            "BibTeX title appears inconsistent with DOI metadata.",
            entry.key,
            {"bib_title": entry.title, "metadata_title": meta.title, "similarity": round(title_score, 3), "doi": entry.doi},
        ))
    if entry.year and meta.year and entry.year != meta.year:
        issues.append(CitationIssue(
            "warning", "doi_year_mismatch",
            "BibTeX year differs from DOI metadata year.",
            entry.key,
            {"bib_year": entry.year, "metadata_year": meta.year, "doi": entry.doi},
        ))
    bib_last = _first_author_last(entry.authors)
    meta_last = _first_author_last(meta.authors or [])
    if bib_last and meta_last and bib_last != meta_last:
        issues.append(CitationIssue(
            "warning", "doi_first_author_mismatch",
            "BibTeX first author differs from DOI metadata first author.",
            entry.key,
            {"bib_first_author": entry.authors[0] if entry.authors else "", "metadata_first_author": (meta.authors or [""])[0], "doi": entry.doi},
        ))
    return md, issues


def audit_project(project: str | Path, online: bool = False, mailto: str | None = None) -> dict[str, Any]:
    root = Path(project).expanduser().resolve()
    manuscript = root / "manuscript"
    tex_files = iter_files(manuscript if manuscript.exists() else root, [".tex"])
    bib_files = iter_files(manuscript if manuscript.exists() else root, [".bib"])
    bib_files = sorted(set(bib_files) | discover_bib_files(tex_files, root))

    cited_keys = extract_citation_keys(tex_files)
    entries, duplicate_keys = parse_bibtex_files(bib_files)
    by_key = {e.key: e for e in entries}
    issues: list[CitationIssue] = []

    for key in sorted(cited_keys - set(by_key)):
        issues.append(CitationIssue("error", "cited_key_missing", "Citation key is used in LaTeX but missing from BibTeX.", key))
    for key in sorted(set(by_key) - cited_keys):
        issues.append(CitationIssue("info", "unused_bib_entry", "BibTeX entry is not cited in current LaTeX files.", key))
    for key in duplicate_keys:
        issues.append(CitationIssue("error", "duplicate_bib_key", "BibTeX key appears more than once.", key))

    doi_to_keys: dict[str, list[str]] = {}
    entry_reports = []
    for entry in entries:
        if not entry.title:
            issues.append(CitationIssue("warning", "missing_title", "BibTeX entry has no title.", entry.key))
        if not entry.year:
            issues.append(CitationIssue("warning", "missing_year", "BibTeX entry has no year/date.", entry.key))
        if entry.doi:
            if not is_plausible_doi(entry.doi):
                issues.append(CitationIssue("error", "malformed_doi", "DOI does not match a standard DOI pattern.", entry.key, {"doi": entry.doi}))
            doi_to_keys.setdefault(entry.doi, []).append(entry.key)
        metadata = None
        online_issues: list[CitationIssue] = []
        if online and entry.doi and is_plausible_doi(entry.doi):
            metadata, online_issues = _verify_entry_online(entry, mailto=mailto)
            issues.extend(online_issues)
        entry_reports.append({
            "key": entry.key,
            "type": entry.entry_type,
            "title": entry.title,
            "year": entry.year,
            "doi": entry.doi,
            "arxiv": _entry_arxiv(entry),
            "authors": entry.authors,
            "metadata": metadata,
        })

    for doi, keys in sorted(doi_to_keys.items()):
        if len(keys) > 1:
            issues.append(CitationIssue("warning", "duplicate_doi", "Multiple BibTeX keys share the same DOI.", ",".join(keys), {"doi": doi, "keys": keys}))

    source_cards, source_issues = _verify_source_cards(root, cited_keys, by_key)
    issues.extend(source_issues)

    summary = {
        "project": str(root),
        "tex_files": len(tex_files),
        "bib_files": len(bib_files),
        "cited_keys": len(cited_keys),
        "bib_entries": len(entries),
        "source_cards": len(source_cards),
        "issues": len(issues),
        "errors": sum(1 for i in issues if i.severity == "error"),
        "warnings": sum(1 for i in issues if i.severity == "warning"),
        "online": online,
    }
    return {"summary": summary, "issues": [asdict(i) for i in issues], "entries": entry_reports, "source_cards": source_cards}


def generate_source_cards(project: str | Path, overwrite: bool = False, cited_only: bool = True) -> Path:
    """Generate conservative source cards from local BibTeX entries.

    This does not claim that a source supports a manuscript sentence. It only
    creates an auditable source-card row so an agent or human can later fill
    `used_for`, `supports_text`, and `verification_status`.
    """
    root = Path(project).expanduser().resolve()
    manuscript = root / "manuscript"
    tex_files = iter_files(manuscript if manuscript.exists() else root, [".tex"])
    bib_files = iter_files(manuscript if manuscript.exists() else root, [".bib"])
    bib_files = sorted(set(bib_files) | discover_bib_files(tex_files, root))
    cited_keys = extract_citation_keys(tex_files)
    entries, _ = parse_bibtex_files(bib_files)

    out = root / "paper_hs" / "state" / "source_cards.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)

    existing: dict[str, dict[str, Any]] = {}
    if out.exists() and not overwrite:
        rows, _ = _load_jsonl(out)
        for row in rows:
            key = str(row.get("bib_key") or "")
            if key:
                existing[key] = row

    cards = existing.copy()
    counter = len(cards) + 1
    for entry in entries:
        if cited_only and entry.key not in cited_keys:
            continue
        if entry.key in cards and not overwrite:
            continue
        venue = entry.fields.get("journal") or entry.fields.get("booktitle") or entry.fields.get("publisher") or ""
        cards[entry.key] = {
            "source_id": f"S{counter:04d}",
            "bib_key": entry.key,
            "title": entry.title,
            "authors": entry.authors,
            "year": entry.year,
            "venue": venue,
            "doi": entry.doi,
            "arxiv_id": _entry_arxiv(entry),
            "url": entry.fields.get("url", ""),
            "verified_by": "existing_bib",
            "verification_status": "unverified",
            "used_for": [],
            "supports_text": "",
            "does_not_support": "",
            "risk": "medium",
        }
        counter += 1

    with out.open("w", encoding="utf-8") as f:
        for key in sorted(cards):
            f.write(json.dumps(cards[key], ensure_ascii=False) + "\n")
    return out


def citation_report_markdown(report: dict[str, Any]) -> str:
    s = report["summary"]
    lines = [
        "# Citation verification report",
        "",
        f"Project: `{s['project']}`",
        "",
        "## Summary",
        "",
        f"- TeX files: {s['tex_files']}",
        f"- BibTeX files: {s['bib_files']}",
        f"- Cited keys: {s['cited_keys']}",
        f"- BibTeX entries: {s['bib_entries']}",
        f"- Source cards: {s.get('source_cards', 0)}",
        f"- Issues: {s['issues']} ({s['errors']} errors, {s['warnings']} warnings)",
        f"- Online metadata checks: {'yes' if s['online'] else 'no'}",
        "",
        "## Issues",
        "",
    ]
    if not report["issues"]:
        lines.append("No issues detected by the current checks.")
    else:
        for issue in report["issues"]:
            key = f" `{issue['key']}`" if issue.get("key") else ""
            lines.append(f"- **{issue['severity']} / {issue['code']}**{key}: {issue['message']}")
            if issue.get("details"):
                lines.append(f"  - Details: `{issue['details']}`")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "A passing citation-key check does not guarantee that the cited source is the intended paper. DOI/title/author/year/source-card mismatches require human review before manuscript submission.",
        "",
        "The key invariant is: manuscript citation key == source_card.bib_key == parsed .bib key, and canonical identifiers in the source card should match DOI/arXiv/title/year metadata.",
    ])
    return "\n".join(lines) + "\n"
