from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Iterable


@dataclass
class BibEntry:
    entry_type: str
    key: str
    fields: dict[str, str] = field(default_factory=dict)
    raw: str = ""

    @property
    def doi(self) -> str:
        return normalize_doi(self.fields.get("doi", ""))

    @property
    def title(self) -> str:
        return clean_latex(self.fields.get("title", ""))

    @property
    def year(self) -> str:
        value = self.fields.get("year") or self.fields.get("date", "")[:4]
        m = re.search(r"\d{4}", value)
        return m.group(0) if m else ""

    @property
    def authors(self) -> list[str]:
        raw = self.fields.get("author", "")
        if not raw:
            return []
        return [clean_latex(x.strip()) for x in re.split(r"\s+and\s+", raw) if x.strip()]


def normalize_doi(value: str) -> str:
    value = clean_latex(value).strip()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value, flags=re.I)
    value = re.sub(r"^doi:\s*", "", value, flags=re.I)
    return value.strip().lower().rstrip('.')


def is_plausible_doi(value: str) -> bool:
    doi = normalize_doi(value)
    return bool(re.match(r"^10\.\d{4,9}/\S+$", doi))


def clean_latex(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and ((value[0] == value[-1] == '"') or (value[0] == '{' and value[-1] == '}')):
        value = value[1:-1]
    value = value.replace("\\&", "&")
    value = re.sub(r"[{}]", "", value)
    value = re.sub(r"\\[a-zA-Z]+\s*", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _balanced_entry(text: str, start: int) -> tuple[str, int] | None:
    i = start
    if text[i] != '@':
        return None
    brace = text.find('{', i)
    paren = text.find('(', i)
    opens = [x for x in [brace, paren] if x != -1]
    if not opens:
        return None
    open_pos = min(opens)
    open_char = text[open_pos]
    close_char = '}' if open_char == '{' else ')'
    depth = 0
    quote = False
    escape = False
    for j in range(open_pos, len(text)):
        ch = text[j]
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if ch == '"':
            quote = not quote
        if quote:
            continue
        if ch == open_char:
            depth += 1
        elif ch == close_char:
            depth -= 1
            if depth == 0:
                return text[i:j+1], j+1
    return None


def _split_top_level(s: str, sep: str = ',') -> list[str]:
    parts: list[str] = []
    depth = 0
    quote = False
    escape = False
    start = 0
    for i, ch in enumerate(s):
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if ch == '"':
            quote = not quote
        if not quote:
            if ch in '{(':
                depth += 1
            elif ch in '})' and depth > 0:
                depth -= 1
            elif ch == sep and depth == 0:
                parts.append(s[start:i].strip())
                start = i + 1
    tail = s[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def parse_bibtex(text: str) -> tuple[list[BibEntry], list[str]]:
    entries: list[BibEntry] = []
    duplicates: list[str] = []
    seen: set[str] = set()
    pos = 0
    while True:
        at = text.find('@', pos)
        if at == -1:
            break
        result = _balanced_entry(text, at)
        if not result:
            pos = at + 1
            continue
        raw, pos = result
        header_end = raw.find('{') if '{' in raw else raw.find('(')
        entry_type = raw[1:header_end].strip().lower()
        body = raw[header_end+1:-1].strip()
        pieces = _split_top_level(body)
        if not pieces:
            continue
        key = pieces[0].strip()
        fields: dict[str, str] = {}
        for piece in pieces[1:]:
            if '=' not in piece:
                continue
            name, value = piece.split('=', 1)
            fields[name.strip().lower()] = clean_latex(value.strip().rstrip(','))
        if key in seen:
            duplicates.append(key)
        seen.add(key)
        entries.append(BibEntry(entry_type=entry_type, key=key, fields=fields, raw=raw))
    return entries, duplicates


def parse_bibtex_files(paths: Iterable) -> tuple[list[BibEntry], list[str]]:
    entries: list[BibEntry] = []
    duplicates: list[str] = []
    seen: set[str] = set()
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        parsed, local_dups = parse_bibtex(text)
        duplicates.extend(local_dups)
        for entry in parsed:
            if entry.key in seen:
                duplicates.append(entry.key)
            seen.add(entry.key)
            entries.append(entry)
    return entries, sorted(set(duplicates))


def format_bibtex_entry(entry: BibEntry, metadata: dict[str, object]) -> str:
    title = str(metadata.get("title") or entry.title)
    year = str(metadata.get("year") or entry.year)
    doi = str(metadata.get("doi") or entry.doi)
    authors = metadata.get("authors") or entry.authors
    if isinstance(authors, list):
        author = " and ".join(str(a) for a in authors)
    else:
        author = str(authors)
    venue = str(metadata.get("venue") or entry.fields.get("journal") or entry.fields.get("booktitle") or "")
    fields = {
        "title": title,
        "author": author,
        "year": year,
    }
    if venue:
        fields["journal" if entry.entry_type == "article" else "booktitle"] = venue
    if doi:
        fields["doi"] = doi
    lines = [f"@{entry.entry_type or 'article'}{{{entry.key},"]
    for k, v in fields.items():
        if v:
            lines.append(f"  {k} = {{{v}}},")
    lines.append("}")
    return "\n".join(lines)
