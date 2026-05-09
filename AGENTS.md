# Repository instructions for Codex

This repository builds Paper Heuristic System, a reusable skill and CLI for iterative paper revision.

## Working rules

- Keep the plug-and-play skill at `.agents/skills/paper_heuristic_system/SKILL.md` valid and concise.
- Keep Python code dependency-light. Prefer the standard library unless there is a clear reason to add a dependency.
- Never write paper-specific state into repository root. Use `templates/paper_project` for reusable skeletons and `workspace/*` for ignored local projects.
- When changing citation verification logic, run `python -m pytest` or `python -m unittest discover tests`.
- Do not make novelty reports sound definitive. They are prior-art risk maps, not proof that an idea is original.
