from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
import json
import time
import urllib.parse
import urllib.request
from typing import Any


@dataclass
class WorkMetadata:
    source: str
    title: str = ""
    doi: str = ""
    year: str = ""
    authors: list[str] | None = None
    venue: str = ""
    url: str = ""
    abstract: str = ""
    cited_by_count: int | None = None
    raw: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "title": self.title,
            "doi": self.doi,
            "year": self.year,
            "authors": self.authors or [],
            "venue": self.venue,
            "url": self.url,
            "abstract": self.abstract,
            "cited_by_count": self.cited_by_count,
        }


def similarity(a: str, b: str) -> float:
    a = " ".join((a or "").lower().split())
    b = " ".join((b or "").lower().split())
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def _json_get(url: str, timeout: int = 20, mailto: str | None = None) -> dict[str, Any]:
    headers = {"User-Agent": "paper-heuristic-system/0.2"}
    if mailto:
        headers["User-Agent"] += f" (mailto:{mailto})"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _names_crossref(authors: list[dict[str, Any]] | None) -> list[str]:
    out = []
    for a in authors or []:
        given = a.get("given", "")
        family = a.get("family", "")
        name = " ".join(x for x in [given, family] if x).strip()
        if name:
            out.append(name)
    return out


def _year_from_crossref(item: dict[str, Any]) -> str:
    for key in ["published-print", "published-online", "published", "issued"]:
        parts = item.get(key, {}).get("date-parts")
        if parts and parts[0]:
            return str(parts[0][0])
    return ""


def crossref_by_doi(doi: str, mailto: str | None = None) -> WorkMetadata | None:
    if not doi:
        return None
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    if mailto:
        url += "?mailto=" + urllib.parse.quote(mailto)
    data = _json_get(url, mailto=mailto)
    item = data.get("message", {})
    titles = item.get("title") or []
    venues = item.get("container-title") or []
    return WorkMetadata(
        source="crossref",
        title=titles[0] if titles else "",
        doi=(item.get("DOI") or "").lower(),
        year=_year_from_crossref(item),
        authors=_names_crossref(item.get("author")),
        venue=venues[0] if venues else "",
        url=item.get("URL", ""),
        raw=item,
    )


def search_crossref(query: str, rows: int = 10, mailto: str | None = None) -> list[WorkMetadata]:
    params = {"query.bibliographic": query, "rows": str(rows)}
    if mailto:
        params["mailto"] = mailto
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    data = _json_get(url, mailto=mailto)
    items = data.get("message", {}).get("items", [])
    works = []
    for item in items:
        titles = item.get("title") or []
        venues = item.get("container-title") or []
        works.append(WorkMetadata(
            source="crossref",
            title=titles[0] if titles else "",
            doi=(item.get("DOI") or "").lower(),
            year=_year_from_crossref(item),
            authors=_names_crossref(item.get("author")),
            venue=venues[0] if venues else "",
            url=item.get("URL", ""),
            raw=item,
        ))
    return works


def _abstract_from_openalex(inv: dict[str, list[int]] | None) -> str:
    if not inv:
        return ""
    pairs = []
    for word, positions in inv.items():
        for pos in positions:
            pairs.append((pos, word))
    pairs.sort()
    return " ".join(word for _, word in pairs)


def _names_openalex(authorships: list[dict[str, Any]] | None) -> list[str]:
    names = []
    for a in authorships or []:
        author = a.get("author", {})
        name = author.get("display_name")
        if name:
            names.append(name)
    return names


def openalex_by_doi(doi: str, mailto: str | None = None) -> WorkMetadata | None:
    if not doi:
        return None
    params = {}
    if mailto:
        params["mailto"] = mailto
    url = "https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="")
    if params:
        url += "?" + urllib.parse.urlencode(params)
    item = _json_get(url, mailto=mailto)
    return _work_from_openalex(item)


def _work_from_openalex(item: dict[str, Any]) -> WorkMetadata:
    primary = item.get("primary_location") or {}
    source = primary.get("source") or {}
    return WorkMetadata(
        source="openalex",
        title=item.get("display_name", ""),
        doi=(item.get("doi") or "").replace("https://doi.org/", "").lower(),
        year=str(item.get("publication_year") or ""),
        authors=_names_openalex(item.get("authorships")),
        venue=source.get("display_name", "") if isinstance(source, dict) else "",
        url=item.get("id", ""),
        abstract=_abstract_from_openalex(item.get("abstract_inverted_index")),
        cited_by_count=item.get("cited_by_count"),
        raw=item,
    )


def search_openalex(query: str, rows: int = 10, mailto: str | None = None) -> list[WorkMetadata]:
    params = {"search": query, "per-page": str(rows)}
    if mailto:
        params["mailto"] = mailto
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    data = _json_get(url, mailto=mailto)
    return [_work_from_openalex(item) for item in data.get("results", [])]


def polite_sleep(seconds: float = 0.1) -> None:
    time.sleep(seconds)


def search_semantic_scholar(query: str, rows: int = 10, api_key: str | None = None) -> list[WorkMetadata]:
    params = {
        "query": query,
        "limit": str(rows),
        "fields": "title,authors,year,venue,url,externalIds,citationCount,abstract",
    }
    url = "https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(params)
    headers = {"User-Agent": "paper-heuristic-system/0.2"}
    if api_key:
        headers["x-api-key"] = api_key
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    works: list[WorkMetadata] = []
    for item in data.get("data", []):
        external = item.get("externalIds") or {}
        works.append(WorkMetadata(
            source="semantic_scholar",
            title=item.get("title", ""),
            doi=(external.get("DOI") or "").lower(),
            year=str(item.get("year") or ""),
            authors=[a.get("name", "") for a in item.get("authors", []) if a.get("name")],
            venue=item.get("venue", ""),
            url=item.get("url", ""),
            abstract=item.get("abstract", "") or "",
            cited_by_count=item.get("citationCount"),
            raw=item,
        ))
    return works


def search_arxiv(query: str, rows: int = 10) -> list[WorkMetadata]:
    import xml.etree.ElementTree as ET
    params = {"search_query": "all:" + query, "start": "0", "max_results": str(rows)}
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "paper-heuristic-system/0.2"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        text = resp.read().decode("utf-8", errors="ignore")
    root = ET.fromstring(text)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    works: list[WorkMetadata] = []
    for entry in root.findall("a:entry", ns):
        title = " ".join((entry.findtext("a:title", default="", namespaces=ns) or "").split())
        abstract = " ".join((entry.findtext("a:summary", default="", namespaces=ns) or "").split())
        published = entry.findtext("a:published", default="", namespaces=ns) or ""
        authors = []
        for author in entry.findall("a:author", ns):
            name = author.findtext("a:name", default="", namespaces=ns)
            if name:
                authors.append(name)
        works.append(WorkMetadata(
            source="arxiv",
            title=title,
            doi="",
            year=published[:4] if len(published) >= 4 else "",
            authors=authors,
            venue="arXiv",
            url=entry.findtext("a:id", default="", namespaces=ns) or "",
            abstract=abstract,
            raw={},
        ))
    return works

