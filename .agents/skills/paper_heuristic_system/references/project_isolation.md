# Project isolation

Every paper project must own its local state.

## Allowed to share

- this repository;
- the plug-and-play skill template;
- generic schemas;
- generic CLI commands;
- public source metadata.

## Never share automatically

- claim graph;
- evidence ledger;
- reviewer issues;
- failed directions;
- decisions;
- author constraints;
- response matrix;
- run history;
- venue-specific strategy inferred from another paper.

## Directory policy

```text
paper-a/.agents/skills/paper_heuristic_system/
paper-a/paper_hs/

paper-b/.agents/skills/paper_heuristic_system/
paper-b/paper_hs/
```

Paper A's state must never be loaded into Paper B unless the user explicitly provides it as source text.
