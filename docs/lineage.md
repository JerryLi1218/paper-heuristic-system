# Lineage

Paper-HS is inspired by Jiayi Weng's [Learning Beyond Gradients](https://trinkle23897.github.io/learning-beyond-gradients/), which develops the Heuristic Learning / Heuristic System framing for coding-agent-maintained software. Paper-HS applies that framing to research writing: the evolving system is a manuscript project with explicit claims, evidence, citations, reviewer issues, regression checks, and memory.

Suggested citation:

```bibtex
@misc{weng2026learning_beyond_gradients,
  title = {Learning Beyond Gradients},
  author = {Weng, Jiayi},
  year = {2026},
  month = may,
  howpublished = {\url{https://trinkle23897.github.io/learning-beyond-gradients/}},
  note = {Blog post}
}
```

This repository condenses the earlier multi-skill Paper-HS prototype into a single plug-and-play skill plus a CLI. The earlier prototype separated controller, ingestion, claim graph extraction, evidence ledger building, reviewer issue mapping, patch generation, regression evaluation, narrative compression, memory management, and meta-skill optimization.

The new distribution keeps those capabilities inside one skill and adds a citation/novelty verification subsystem.
