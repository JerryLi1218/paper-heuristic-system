# Paper revision workflow

## State files

```text
paper_hs/state/claim_graph.json
paper_hs/state/evidence_ledger.json
paper_hs/state/reviewer_issues.jsonl
paper_hs/state/source_cards.jsonl
paper_hs/state/section_interfaces.json
paper_hs/state/terminology.json
```

## Revision modes

- `ingest`: build state, no rewriting.
- `diagnose`: identify broken claim/evidence/section/reviewer/citation links.
- `plan`: choose minimal patch or macro-patch.
- `patch`: modify manuscript.
- `evaluate`: run regression checks.
- `compress`: integrate accepted local patches into coherent narrative.
- `respond`: align response letter with actual manuscript changes.

## Minimal patch rule

A patch is valid only when it has:

- target issue or target claim;
- reason for intervention;
- changed locations;
- expected improvement;
- regression checks;
- rollback condition.

## Regression checks

- Strong claims must have evidence IDs.
- Abstract/introduction/conclusion must not disagree.
- Related-work contrast must cite verified source cards.
- Response letter must point to actual manuscript changes.
- Terminology and notation definitions must precede use.
- Limitations and boundary conditions must not disappear.
