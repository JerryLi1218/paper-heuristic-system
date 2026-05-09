# Skill: Claim Graph Extractor

## Mission

从论文中抽取核心主张，并建立 claim 之间、claim 与 evidence 之间、claim 与章节之间的依赖图。它是防止论文多轮修改后语义漂移的核心 skill。

## When to invoke

- 初次接入论文。
- 摘要、引言、贡献列表、结论发生修改。
- 审稿人质疑 novelty、validity、scope、generalization。
- 论文被压缩或扩展后需要重新校准 claim 强度。

## Inputs

- manuscript text。
- section_interfaces.json。
- evidence_ledger.json，可为空。
- author constraints。

## Outputs

```text
state/claim_graph.json
reports/claim_risk_report.md
```

## Claim categories

- central_claim：论文主张的核心。
- contribution_claim：贡献列表中的主张。
- empirical_claim：实验结果或 benchmark 结论。
- theoretical_claim：定理、证明、性质、复杂度。
- positioning_claim：相对 prior work 的 novelty boundary。
- limitation_claim：适用范围与限制。
- methodological_claim：方法设计动机。

## Claim strength levels

```text
descriptive    只描述本文做了什么
bounded        在明确条件内成立
comparative    与 baseline / prior work 比较
strong         有广泛外推或显著 superiority 暗示
speculative    推测、启发、future implication
```

## Extraction routine

1. 从 abstract、intro、conclusion 先抽 central 和 contribution claims。
2. 从 method、theory、experiments 抽 support claims。
3. 给每个 claim 分配唯一 ID：C001、C002...
4. 记录 claim 文本、位置、强度、证据、依赖、风险。
5. 检查重复 claim、漂移 claim、过强 claim、孤立 claim。
6. 输出 claim_risk_report，列出 unsupported 或 over-claimed 项。

## Claim object

```json
{
  "claim_id": "C001",
  "text": "The proposed method improves sample efficiency under sparse rewards.",
  "category": "empirical_claim",
  "strength": "bounded",
  "locations": ["abstract", "introduction:p3", "experiments:table2"],
  "evidence_ids": ["E003"],
  "depends_on": ["C004"],
  "risk": "high",
  "status": "supported",
  "allowed_edits": ["narrow", "clarify", "move"],
  "forbidden_edits": ["strengthen_without_new_evidence"]
}
```

## Regression questions

- 修改后 C001 是否仍被 E003 支撑？
- abstract 的 C001 与 conclusion 的 C001 是否同义？
- contribution claim 是否被 experiments 或 theory 支撑？
- 是否出现了 evidence ledger 中不存在的新事实？

## Guardrails

- 没有证据时，claim status 只能是 `unsupported`、`needs_evidence` 或 `should_downgrade`。
- 不把“更有说服力”的表达自动视为更好的表达；先看证据强度。
- 不让 limitation claim 在压缩中消失。
