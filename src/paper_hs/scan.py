from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .project import iter_files
from .latex import extract_citation_keys
from .bibtex import parse_bibtex_files


def scan_project(project: str | Path) -> dict[str, Any]:
    root = Path(project).expanduser().resolve()
    manuscript = root / "manuscript"
    base = manuscript if manuscript.exists() else root
    tex = iter_files(base, [".tex"])
    md = iter_files(base, [".md"])
    bib = iter_files(base, [".bib"])
    entries, dups = parse_bibtex_files(bib)
    return {
        "project": str(root),
        "tex_files": [str(p.relative_to(root)) for p in tex if p.is_relative_to(root)],
        "markdown_files": [str(p.relative_to(root)) for p in md if p.is_relative_to(root)],
        "bib_files": [str(p.relative_to(root)) for p in bib if p.is_relative_to(root)],
        "citation_keys": sorted(extract_citation_keys(tex)),
        "bib_entry_count": len(entries),
        "duplicate_bib_keys": dups,
    }


def scan_markdown(scan: dict[str, Any]) -> str:
    lines = ["# Paper-HS scan report", "", f"Project: `{scan['project']}`", ""]
    for key in ["tex_files", "markdown_files", "bib_files"]:
        lines.append(f"## {key}")
        lines.append("")
        vals = scan.get(key) or []
        if vals:
            lines.extend(f"- `{v}`" for v in vals)
        else:
            lines.append("None detected.")
        lines.append("")
    lines.append(f"Citation keys detected: {len(scan.get('citation_keys') or [])}")
    lines.append(f"BibTeX entries detected: {scan.get('bib_entry_count', 0)}")
    if scan.get("duplicate_bib_keys"):
        lines.append(f"Duplicate BibTeX keys: {', '.join(scan['duplicate_bib_keys'])}")
    return "\n".join(lines) + "\n"
