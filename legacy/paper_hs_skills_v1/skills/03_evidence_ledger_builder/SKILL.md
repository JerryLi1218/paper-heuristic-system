# Skill: Evidence Ledger Builder

## Mission

为论文中的 claims 建立证据账本。证据包括实验结果、表格、图、定理、证明、消融、引用、数据集说明、人工标注规则和负结果。Evidence Ledger 是防止幻觉式增强 claim 的主防线。

## When to invoke

- 初次接入论文。
- 新增实验、图表、定理、引用。
- 审稿人质疑 evidence sufficiency。
- 需要判断某个 claim 是否可以增强或必须降级。

## Inputs

- manuscript。
- tables、figures、appendix、bib。
- raw results 或实验记录，如用户提供。
- source_cards.jsonl。

## Outputs

```text
state/evidence_ledger.json
state/source_cards.jsonl
reports/evidence_gap_report.md
```

## Evidence types

- experiment_result
- ablation
- theorem
- proof
- citation
- dataset_description
- qualitative_example
- negative_result
- implementation_detail
- human_evaluation

## Evidence object

```json
{
  "evidence_id": "E003",
  "type": "experiment_result",
  "source_location": "Table 2",
  "summary": "Method A achieves higher success rate than baselines on 5 sparse-reward tasks.",
  "supports_claims": ["C001", "C007"],
  "conditions": ["5 tasks", "same environment-step budget", "3 seeds"],
  "limitations": ["no wall-clock comparison", "limited task diversity"],
  "strength": "moderate",
  "verifiability": "internal_table",
  "status": "available"
}
```

## Source card object

```json
{
  "source_id": "S012",
  "bib_key": "smith2024method",
  "title": "...",
  "authors": ["..."],
  "venue_year": "ICLR 2024",
  "used_for": ["related work contrast", "baseline definition"],
  "exact_support": "Defines the benchmark setting used in Table 2.",
  "risk": "low",
  "verified": true
}
```

## Procedure

1. 抽取所有显性证据位置。
2. 将 evidence 绑定到 claim_graph 中的 claims。
3. 标注证据适用条件，不允许把局部 evidence 外推成全局 claim。
4. 对每个 strong/comparative claim 检查是否至少有一个证据。
5. 识别 citation 被用作背景、方法定义、novelty contrast 或结果支持。
6. 输出 evidence_gap_report。

## Guardrails

- 没有 source card 的新增引用不得进入正文。
- citation 不能替代本文自己的实验结果，除非 claim 是关于 prior work 的描述。
- 表格数字、metric、dataset 名称必须与原稿或用户提供材料一致。
- 对负结果和 limitation 保留账本记录，不能在叙事压缩时自动删除。
