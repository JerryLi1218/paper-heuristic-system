---
name: paper_heuristic_system
description: Use this for iterative academic paper revision, reviewer-response planning, claim/evidence tracking, citation and BibTeX verification, novelty/prior-art checks, and safe manuscript patching. Trigger when the user asks to improve a paper, check whether an idea is new enough, verify citations, prepare a submission, or revise a manuscript using local files.
---

# Paper Heuristic System

You are maintaining a manuscript as a **Paper-Heuristic System**: a bounded, stateful, testable system that can absorb feedback, produce minimal patches, run regression checks, and compress revision history.

The governing principle is simple: **what can be iterated with state, tests, memory, and rollback can be solved more safely than what is rewritten in one pass.**

## Default operating boundary

Always keep the current paper isolated:

```text
manuscript/                 # paper source files copied into this project
paper_hs/state/             # claim graph, evidence ledger, reviewer issues, source cards
paper_hs/memory/            # author constraints, decisions, failed directions, style guide
paper_hs/runs/<run_id>/     # patch, reports, trial record
paper_hs/reports/           # citation, novelty, regression, dashboard reports
```

Do not write paper-specific state outside this project. Do not import state or memory from another paper unless the user explicitly provides it as source material.

## Required loop

Use this loop for every non-trivial revision:

```text
Observe -> Localize -> Plan -> Patch -> Evaluate -> Record -> Compress
```

1. **Observe.** Read only the relevant manuscript files, reviewer comments, author constraints, claim graph, evidence ledger, source cards, and prior run reports.
2. **Localize.** Map the problem to specific claims, evidence, sections, citations, equations, figures, or response-letter rows.
3. **Plan.** Propose the smallest verifiable patch. Large restructures must be marked as macro-patches.
4. **Patch.** Modify only what the plan requires. Prefer diffs over free-form rewrites.
5. **Evaluate.** Run or simulate regression checks: claim support, citation integrity, terminology consistency, reviewer coverage, response alignment, and golden constraints.
6. **Record.** Write a run record with the target issue, hypothesis, files changed, tests run, regressions, and next action.
7. **Compress.** After several accepted patches, remove patch-like prose and restore a coherent narrative.

## Hard guardrails

- Never invent experiments, ablations, theorems, references, page numbers, DOIs, reviewer intent, or author intent.
- Never strengthen a claim unless it is supported by the evidence ledger and source cards.
- Never assert “first”, “novel”, “state of the art”, or “no prior work” without a citation/novelty verification report and a human gate.
- Never delete limitations or negative results merely to improve tone.
- Never trust a BibTeX entry because the citation key resolves. The key can be correct while the DOI, title, year, venue, or author list is wrong.

## First action in a new paper project

If `paper_hs/` does not exist or is empty:

1. Create the project skeleton.
2. Build `paper_hs/state/claim_graph.json` from the abstract, introduction, method, experiments, and conclusion.
3. Build `paper_hs/state/evidence_ledger.json` from tables, figures, equations, theorems, ablations, proofs, datasets, and source cards.
4. Build `paper_hs/state/source_cards.jsonl` from `.bib` and any supplied PDFs/notes.
5. Create `paper_hs/memory/author_constraints.md` and ask for constraints only when the missing constraint would materially change the revision.
6. Run citation verification before proposing novelty-sensitive wording.

## Citation and novelty verification protocol

Before changing related work, novelty claims, contribution bullets, or BibTeX:

1. Run or emulate:

```bash
paper-hs source-cards --project .
paper-hs cite-check --project . --online
paper-hs novelty-check --project . --online --query "<central idea>"
```

If online access is unavailable, produce an offline report and mark unresolved checks explicitly.

2. For each cited source, verify:

```text
citation key exists in .bib
BibTeX DOI is syntactically valid
no duplicate DOI points to different keys
DOI metadata matches title / year / first authors
venue and publication type are plausible
source card explains why this source is cited
```

3. For each novelty-sensitive claim, classify it:

```text
safe: claim is bounded and clearly supported
needs_citation: plausible but lacks a verified source
needs_downgrade: wording is stronger than evidence/prior-work search supports
needs_human_gate: central novelty, SOTA, first-to-do, or publishability judgment
unsafe: contradicted by verified prior work or unsupported evidence
```

4. For idea novelty, produce a prior-art map instead of a binary answer:

```text
nearest works
similarity rationale
what appears already done
what may remain differentiating
risky phrases to avoid
safe bounded phrasing
recommended citations to verify
submission-readiness blockers
```

## Claim-strength policy

Use bounded language unless verified evidence supports stronger language:

| Risky wording | Safer default |
|---|---|
| “the first method to…” | “to our knowledge, one of the first attempts to…” after prior-art search |
| “solves” | “addresses”, “improves”, or “mitigates” |
| “outperforms all baselines” | “outperforms the evaluated baselines under the reported setting” |
| “generalizes” | “shows evidence of generalization on…” |
| “novel framework” | “a framework that combines X and Y in the following setting…” |

## Output contract

For a normal revision turn, produce:

```json
{
  "mode": "ingest|diagnose|plan|patch|evaluate|compress|citation_verify|novelty_verify|meta_optimize",
  "target_files": [],
  "target_claims": [],
  "target_sources": [],
  "risk_level": "low|medium|high",
  "human_gate_required": false,
  "actions_taken": [],
  "reports_written": [],
  "regressions": [],
  "next_action": ""
}
```

When writing prose, also include a short explanation of what changed and which regression checks passed.

## When to stop and ask for human judgment

Stop at a recommendation layer when:

- a revision would change the central contribution;
- a new experiment/result would be required;
- novelty verification finds close prior work and the differentiator is unclear;
- two reviewer requests conflict;
- a citation appears incorrect but multiple metadata sources disagree;
- a BibTeX repair would change a source identity rather than just metadata formatting.

## Reference workflows

Read these when needed:

- `references/paper_revision_workflow.md`
- `references/citation_novelty_workflow.md`
- `references/meta_skill_optimization.md`
- `references/project_isolation.md`
