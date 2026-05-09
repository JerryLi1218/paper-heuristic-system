# Design

Paper-HS applies a systems-engineering view to manuscript revision. A paper is not just text; it is a coupled system of claims, evidence, citations, reviewer issues, author constraints, venue expectations, and revision history.

## Why state matters

Without explicit state, an agent tends to revise locally and forget global constraints. Paper-HS externalizes the state so iteration becomes inspectable:

- claim graph prevents claim drift;
- evidence ledger prevents unsupported strengthening;
- source cards prevent citation hallucination;
- regression checks prevent old fixes from being broken;
- memory prevents repeated dead ends;
- narrative compression prevents patch accumulation.

## Coupling complexity

The difficulty of revising a paper is not proportional to page count. It is proportional to coupling:

```text
claim <-> evidence
claim <-> citation
reviewer issue <-> section
abstract <-> conclusion
source identity <-> BibTeX metadata
local patch <-> global narrative
```

The system reduces coupling by assigning IDs, maintaining ledgers, and testing after patches.

## Citation verification as a subsystem

Citation verification is treated as a first-class subsystem because paper agents often get the citation path right but the bibliographic identity wrong. The system checks both:

```text
LaTeX citation key integrity
BibTeX entry identity
DOI metadata identity
source-card usage rationale
claim-source alignment
```

## Novelty verification as prior-art mapping

Novelty cannot be mechanically proved by a metadata search. The workflow therefore produces a prior-art risk map and asks the human author to decide whether the remaining differentiator is real.
