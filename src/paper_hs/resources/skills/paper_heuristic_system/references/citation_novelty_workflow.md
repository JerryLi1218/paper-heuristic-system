# Citation and novelty workflow

## Citation verification

Use the CLI when available:

```bash
paper-hs source-cards --project .
paper-hs cite-check --project . --online --mailto you@example.com
```

Offline checks:

- citation keys used in LaTeX exist in `.bib`;
- `.bib` keys are not duplicated;
- cited keys are not accidentally unused/missing;
- DOI syntax is plausible;
- duplicate DOIs do not create multiple inconsistent entries;
- title/year fields are present when needed.

Online checks:

- DOI metadata from Crossref/OpenAlex;
- BibTeX title similarity to DOI title;
- first-author and year agreement;
- possible wrong DOI copied into right key;
- suggested canonical BibTeX repair.

## Novelty verification

Use the CLI when available:

```bash
paper-hs novelty-check --project . --online --query "one-sentence idea"
```

Return a prior-art map:

```text
nearest works
why they are close
which parts of the idea are already present
which differentiators may remain
claim wording to downgrade
citations to add or verify
submission-readiness blockers
```

## Publishability risk rubric

- **Low risk:** contribution is bounded, prior-art map has no close match, evidence supports claim strength.
- **Medium risk:** close adjacent work exists; contribution must be framed with clearer boundary and citations.
- **High risk:** near-identical work exists, SOTA/first claims are unsupported, or key citations are wrong.

## Wording rules

- Use “to our knowledge” only after search logs exist.
- Replace broad novelty claims with exact mechanism/setting/dataset/task scope.
- Cite the closest prior work, not only friendly or older work.
- If a source is used for a method/history claim, verify that the source actually says that.

## Source-card invariant

For every cited source used in a claim-sensitive sentence, maintain this invariant:

```text
manuscript citation key == source_card.bib_key == parsed .bib key
source_card DOI/arXiv/title/year ~= local BibTeX DOI/arXiv/title/year
```

This catches the common error where the agent found the right paper path but generated or edited the wrong BibTeX record.
