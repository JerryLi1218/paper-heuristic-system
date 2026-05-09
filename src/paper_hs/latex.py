from __future__ import annotations

import re
from pathlib import Path

CITE_COMMANDS = [
    "cite", "citep", "citet", "citealp", "citeauthor", "citeyear", "citeyearpar",
    "parencite", "textcite", "autocite", "supercite", "footcite", "smartcite",
    "citealt", "Cite", "Citep", "Citet",
]

CITE_RE = re.compile(
    r"\\(?P<cmd>" + "|".join(re.escape(c) for c in CITE_COMMANDS) + r")\*?"
    r"(?:\s*\[[^\]]*\]){0,2}\s*\{(?P<keys>[^}]+)\}",
    re.MULTILINE,
)

BIB_RE = re.compile(r"\\(?:bibliography|addbibresource)\s*(?:\[[^\]]*\])?\s*\{(?P<files>[^}]+)\}")


def strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        out = []
        escaped = False
        for ch in line:
            if ch == "\\" and not escaped:
                escaped = True
                out.append(ch)
                continue
            if ch == "%" and not escaped:
                break
            out.append(ch)
            escaped = False
        lines.append("".join(out))
    return "\n".join(lines)


def extract_citation_keys_from_text(text: str) -> set[str]:
    text = strip_comments(text)
    keys: set[str] = set()
    for match in CITE_RE.finditer(text):
        for key in match.group("keys").split(','):
            k = key.strip()
            if k:
                keys.add(k)
    return keys


def extract_citation_keys(paths: list[Path]) -> set[str]:
    keys: set[str] = set()
    for path in paths:
        try:
            keys |= extract_citation_keys_from_text(path.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
    return keys


def discover_bib_files(tex_paths: list[Path], project_root: Path) -> set[Path]:
    bibs: set[Path] = set()
    for path in tex_paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in BIB_RE.finditer(strip_comments(text)):
            for raw in match.group("files").split(','):
                name = raw.strip().strip('{}')
                if not name:
                    continue
                candidates = []
                if name.endswith('.bib'):
                    candidates.append(path.parent / name)
                    candidates.append(project_root / name)
                else:
                    candidates.append(path.parent / f"{name}.bib")
                    candidates.append(project_root / f"{name}.bib")
                for c in candidates:
                    if c.exists():
                        bibs.add(c.resolve())
    return bibs
