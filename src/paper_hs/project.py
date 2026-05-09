from __future__ import annotations

import json
import shutil
from importlib import resources
from pathlib import Path
from typing import Iterable, Protocol, runtime_checkable

from .paths import project_root

REPO_ROOT = Path(__file__).resolve().parents[2]


@runtime_checkable
class TraversableLike(Protocol):
    name: str
    def iterdir(self): ...
    def is_dir(self) -> bool: ...
    def is_file(self) -> bool: ...
    def read_bytes(self) -> bytes: ...


def _repo_path_or_resource(repo_relative: str, resource_relative: str):
    """Return a repository path in editable mode, otherwise a packaged resource."""
    repo_path = REPO_ROOT / repo_relative
    if repo_path.exists():
        return repo_path
    return resources.files("paper_hs").joinpath("resources", *resource_relative.split("/"))


def _template_source():
    return _repo_path_or_resource("templates/paper_project", "templates/paper_project")


def _skill_source():
    return _repo_path_or_resource(".agents/skills/paper_heuristic_system", "skills/paper_heuristic_system")


def copytree_merge(src, dst: Path, overwrite: bool = False) -> None:
    """Copy a filesystem or package-resource directory into dst.

    Existing files are preserved unless overwrite=True. This keeps project-local
    state stable while still allowing the same CLI to work from editable installs,
    source distributions, and wheels.
    """
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            copytree_merge(item, target, overwrite=overwrite)
        elif item.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            if overwrite or not target.exists():
                target.write_bytes(item.read_bytes())


def init_project(project: str | Path, title: str = "Untitled Paper", venue: str = "unknown", source: str | Path | None = None) -> Path:
    root = project_root(project)
    root.mkdir(parents=True, exist_ok=True)
    copytree_merge(_template_source(), root)

    config = {
        "title": title,
        "venue": venue,
        "created_by": "paper-hs",
        "state_policy": "project-local-only",
    }
    config_path = root / "paper_hs" / "project_config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if source:
        src = Path(source).expanduser().resolve()
        dst = root / "manuscript"
        dst.mkdir(parents=True, exist_ok=True)
        ignored_names = {"paper_hs", ".paper-hs", ".agents", ".git", "__pycache__", ".pytest_cache"}
        ignored_suffixes = {".aux", ".bbl", ".blg", ".log", ".out", ".toc", ".fls", ".fdb_latexmk", ".synctex.gz"}

        def should_skip(path: Path) -> bool:
            if path.name in ignored_names:
                return True
            return any(str(path).endswith(suffix) for suffix in ignored_suffixes)

        if src.is_dir():
            for item in src.iterdir():
                if should_skip(item):
                    continue
                target = dst / item.name
                if item.is_dir():
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.copytree(item, target, ignore=lambda d, names: [n for n in names if n in ignored_names])
                else:
                    shutil.copy2(item, target)
        elif src.is_file():
            if not should_skip(src):
                shutil.copy2(src, dst / src.name)
        else:
            raise FileNotFoundError(f"source does not exist: {src}")
    return root


def install_skill(target: str | Path, overwrite: bool = False) -> Path:
    root = project_root(target)
    dst = root / ".agents" / "skills" / "paper_heuristic_system"
    if dst.exists() and overwrite:
        shutil.rmtree(dst)
    if dst.exists() and not overwrite:
        return dst
    copytree_merge(_skill_source(), dst, overwrite=True)
    return dst


def iter_files(root: str | Path, suffixes: Iterable[str]) -> list[Path]:
    p = Path(root)
    suff = {s.lower() for s in suffixes}
    return [x for x in p.rglob("*") if x.is_file() and x.suffix.lower() in suff]
