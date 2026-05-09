from __future__ import annotations

from pathlib import Path


def project_root(path: str | Path) -> Path:
    root = Path(path).expanduser().resolve()
    return root


def paper_hs_dir(project: str | Path) -> Path:
    return project_root(project) / "paper_hs"


def manuscript_dir(project: str | Path) -> Path:
    return project_root(project) / "manuscript"


def reports_dir(project: str | Path) -> Path:
    return paper_hs_dir(project) / "reports"


def state_dir(project: str | Path) -> Path:
    return paper_hs_dir(project) / "state"
