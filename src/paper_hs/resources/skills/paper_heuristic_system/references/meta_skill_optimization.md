# Meta-skill optimization

The skill system itself is a heuristic system. When the workflow repeatedly fails, update the skill locally instead of merely prompting harder.

## Observe

Collect failure cases:

- repeated hallucinated citation;
- repeated over-strong novelty wording;
- patch fixes one reviewer issue but breaks another;
- response letter diverges from manuscript;
- citation key resolves but BibTeX metadata is wrong;
- memory grows without compression.

## Localize

Map failure to one of:

```text
skill instruction
workflow reference
schema
CLI check
state representation
human gate
memory rule
```

## Patch

Make the smallest local skill patch. Do not change the global template unless this failure appears across multiple papers.

## Regression

Add a golden case so the failure does not recur.
