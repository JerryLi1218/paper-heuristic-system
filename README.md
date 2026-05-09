# Paper Heuristic System

[中文说明](README.zh-CN.md)


**Paper Heuristic System (Paper-HS)** turns manuscript revision into an iterative, testable engineering loop.

It is built for researchers who already have a paper draft and want an agent-assisted workflow that can:

- revise an existing paper without losing the author’s real claims;
- track claims, evidence, reviewer issues, source cards, decisions, and failed directions;
- run regression checks after every patch;
- verify citations and BibTeX metadata;
- map prior work around an idea before asserting novelty;
- keep every paper project isolated so memory from one paper does not pollute another.

The repository includes a **single plug-and-play Codex skill**, an optional Codex plugin manifest, and a small Python CLI. You can use the skill alone, the CLI alone, or both together.

## 30-second setup

```bash
git clone https://github.com/JerryLi1218/paper-heuristic-system.git
cd paper-heuristic-system
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Create an isolated workspace for a paper:

```bash
paper-hs init --project ./workspace/my-paper --title "My Paper" --venue "ICLR" --source /path/to/my/paper
```

Install the plug-and-play skill into that paper project:

```bash
paper-hs install-skill --target ./workspace/my-paper
```

Open Codex from the paper project:

```bash
cd ./workspace/my-paper
codex
```

Then ask Codex:

```text
Use the paper_heuristic_system skill. Ingest this paper, build the claim graph and evidence ledger, then run citation verification before proposing any revision.
```

## Core loop

Paper-HS treats a manuscript as a maintained system:

```text
Observe -> Localize -> Plan -> Patch -> Evaluate -> Record -> Compress
```

Every modification should update both the manuscript and the system state:

```text
paper_hs/state/claim_graph.json
paper_hs/state/evidence_ledger.json
paper_hs/state/reviewer_issues.jsonl
paper_hs/state/source_cards.jsonl
paper_hs/memory/decisions.md
paper_hs/memory/failed_directions.md
paper_hs/runs/<run_id>/patch.diff
paper_hs/runs/<run_id>/regression_report.md
paper_hs/runs/<run_id>/revision_trial.json
```

## Citation and novelty verification

The added verification subsystem addresses four common paper-writing failures:

1. **“Is this idea new enough?”**  
   Run a novelty landscape search using Crossref/OpenAlex/Semantic Scholar/arXiv metadata and produce a prior-art risk report.

2. **“Has someone already done this?”**  
   Search scholarly metadata from your idea statement and core claims, then rank nearby works by textual overlap.

3. **“Can I safely say this in a submission?”**  
   Check whether novelty, first-to-do, SOTA, and broad empirical claims are supported by evidence and prior-work search logs.

4. **“Are my citations and BibTeX entries correct?”**  
   Parse LaTeX citations and `.bib` files, check missing/unused keys, duplicate DOIs, malformed DOIs, DOI-to-title mismatches, author/year mismatches, source-card-to-bib-key drift, and source-card title/year/DOI/arXiv mismatches.

Typical commands:

```bash
paper-hs source-cards --project ./workspace/my-paper
paper-hs cite-check --project ./workspace/my-paper --online --mailto you@example.com
paper-hs novelty-check --project ./workspace/my-paper --online --query "my central idea in one sentence"
paper-hs verify --project ./workspace/my-paper --online --mailto you@example.com
```

Online checks use public scholarly metadata APIs. Offline mode still catches citation-key, duplicate DOI, malformed BibTeX, and source-card consistency problems. `source-cards` bootstraps conservative source cards from local BibTeX entries; humans or agents should then fill `usage` and `supports_claims`.

## Why one total skill?

Large skill suites are powerful but cumbersome for distribution. This repository ships a single Codex skill:

```text
.agents/skills/paper_heuristic_system/SKILL.md
```

That skill contains the whole operating protocol and refers to compact workflow references inside the same skill directory. It can be copied into any repo or installed with:

```bash
paper-hs install-skill --target /path/to/paper-project
```

## Codex plugin manifest

For plugin-style distribution, the repository also includes:

```text
.codex-plugin/plugin.json
```

The manifest points to the bundled `./skills/` directory, while `.agents/skills/` remains available for repo-local Codex discovery. The same repository can therefore be copied as a skill pack or published as a plugin-style GitHub project.

## Project isolation rule

Every paper gets its own `paper_hs/` state directory and its own local skill copy:

```text
paper-a/
  .agents/skills/paper_heuristic_system/
  paper_hs/

paper-b/
  .agents/skills/paper_heuristic_system/
  paper_hs/
```

Do not share `state/`, `memory/`, `runs/`, or `reports/` between papers. Only the repository template and skill definition are reusable.

## Repository layout

```text
.agents/skills/paper_heuristic_system/   # Plug-and-play Codex skill
src/paper_hs/                            # Python CLI and verification logic
templates/paper_project/                 # Isolated project skeleton
examples/minimal_latex/                  # Tiny example paper
docs/                                    # Design notes and workflow guides
tests/                                   # Stdlib pytest/unittest tests
```

## Safety boundaries

Paper-HS can help discover prior work and detect risky claims, but it does not prove novelty. Treat novelty reports as structured evidence for human judgment. The system must not invent experimental results, fake references, fabricate reviewer intent, or strengthen claims beyond the evidence ledger.
