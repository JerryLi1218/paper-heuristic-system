# Skill: Citation Source Guard

## Mission

约束所有新增引用、外部事实、相关工作表述和 benchmark 描述。它防止论文在修改中出现 citation hallucination 或不当归因。

## When to invoke

- 新增或替换 citation。
- 修改 related work。
- response letter 中引用外部工作。
- 审稿人要求补充 prior work。

## Inputs

- bibliography。
- source_cards.jsonl。
- candidate sources supplied by user or retrieved by an approved search process。
- target claim。

## Outputs

```text
state/source_cards.jsonl
reports/citation_guard_report.md
```

## Source card required fields

```json
{
  "source_id": "S001",
  "bib_key": "",
  "title": "",
  "authors": [],
  "year": "",
  "venue": "",
  "source_type": "paper|dataset|software|standard|webpage",
  "verified_by": "user|search|existing_bib",
  "used_for": [],
  "supports_text": "",
  "limits": "",
  "risk": "low|medium|high"
}
```

## Citation use types

- background
- method_definition
- benchmark_definition
- baseline_source
- novelty_contrast
- empirical_comparison
- limitation_context

## Procedure

1. 对每个新增 citation 建 source card。
2. 标注 citation 能支持什么，不能支持什么。
3. 检查正文中是否过度归因。
4. 检查 bib key 是否存在。
5. 对争议性或近期事实要求更高验证。

## Guardrails

- 不编造 bib key。
- 不用二手总结替代原论文，除非明确标注。
- 不让 citation 承担它无法承担的 claim。
- 不把“相关”误写成“首次提出”。
