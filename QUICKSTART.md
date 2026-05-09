# Quickstart

## 1. Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## 2. Initialize a paper project

```bash
paper-hs init \
  --project ./workspace/my-paper \
  --title "My Paper" \
  --venue "ACL" \
  --source /absolute/path/to/existing/paper
```

This creates an isolated structure:

```text
workspace/my-paper/
  manuscript/
  paper_hs/state/
  paper_hs/memory/
  paper_hs/runs/
  paper_hs/reports/
```

## 3. Install the plug-and-play skill

```bash
paper-hs install-skill --target ./workspace/my-paper
```

## 4. Run baseline checks

```bash
paper-hs scan --project ./workspace/my-paper
paper-hs source-cards --project ./workspace/my-paper
paper-hs cite-check --project ./workspace/my-paper
```

## 5. Use Codex

Start Codex inside the paper project:

```bash
cd ./workspace/my-paper
codex
```

Prompt:

```text
Use the paper_heuristic_system skill. First ingest the manuscript and build state. Do not rewrite the paper yet. Then run citation verification and produce a prioritized revision plan.
```

## 6. Run online citation + novelty checks

```bash
paper-hs cite-check --project ./workspace/my-paper --online --mailto you@example.com
paper-hs novelty-check --project ./workspace/my-paper --online --query "one-sentence central idea" --mailto you@example.com
```

## 7. For another paper

Repeat steps 2–6 with a different project directory. Do not reuse `paper_hs/state`, `paper_hs/memory`, or `paper_hs/runs`.
