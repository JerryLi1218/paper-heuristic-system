# Citation and novelty verification

## Inputs

- LaTeX source files;
- BibTeX files;
- `paper_hs/state/claim_graph.json`;
- `paper_hs/state/source_cards.jsonl`;
- an optional idea statement in `paper_hs/idea.md`.

## Outputs

```text
paper_hs/state/source_cards.jsonl
paper_hs/reports/citation_report.md
paper_hs/reports/citation_report.json
paper_hs/reports/novelty_report.md
paper_hs/reports/novelty_report.json
```

## What is checked

### Citation integrity

- cited key missing from `.bib`;
- duplicate BibTeX key;
- unused BibTeX entries;
- duplicate DOI;
- malformed DOI;
- missing title/year;
- DOI-title mismatch;
- DOI-author mismatch;
- DOI-year mismatch;
- source-card `bib_key` missing from `.bib`;
- source-card title/year/DOI/arXiv mismatch with the local `.bib`;
- cited keys without source cards;
- `citation_claims.jsonl` source_id-to-bib_key drift.

### Novelty landscape

- nearest works from OpenAlex, Crossref, Semantic Scholar, and arXiv when online mode is enabled;
- similarity against title and available abstract metadata;
- likely already-done elements;
- remaining possible differentiators;
- risky novelty language;
- safer bounded alternatives.

## Agent path versus BibTeX key

The verifier enforces a three-identifier discipline:

```text
source_id      stable Paper-HS ID, e.g. S004
canonical_id   DOI / arXiv / URL / OpenReview / ACL ID
bib_key        exact key parsed from the local .bib file
```

This catches the common case where an agent finds the correct paper path but writes a wrong BibTeX key or copies metadata from a different paper.

## Human gate

Any claim of the form below requires a human gate after verification:

```text
first / novel / state-of-the-art / no prior work / solves / generalizes / comprehensive
```

## Source-card bootstrap

Run this before citation verification when `source_cards.jsonl` is empty:

```bash
paper-hs source-cards --project ./workspace/my-paper
```

Generated cards are conservative. They copy local BibTeX metadata and mark each source as `unverified`; they do not assert that the paper supports a specific sentence until `used_for` and `supports_text` are filled.
