#!/usr/bin/env python3
from __future__ import annotations

import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
skill = root / ".agents" / "skills" / "paper_heuristic_system"
out = root / "paper_heuristic_system.skill.zip"
if out.exists():
    out.unlink()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for path in skill.rglob("*"):
        z.write(path, path.relative_to(skill.parent.parent))
print(out)
