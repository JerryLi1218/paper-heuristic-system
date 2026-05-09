# Skill: Regression Evaluator

## Mission

检查一次论文修改是否破坏旧能力。这里的“旧能力”包括：核心 claim、证据绑定、引用完整性、术语一致性、response 覆盖、作者约束、venue 约束。

## When to invoke

- 每次 patch 后。
- 每次 narrative compression 后。
- 每次 response letter 生成后。
- 合并分支前。

## Inputs

- patch.diff。
- manuscript before/after。
- claim_graph.json。
- evidence_ledger.json。
- reviewer_issues.jsonl。
- source_cards.jsonl。
- golden_constraints.md。

## Outputs

```text
runs/<run_id>/regression_report.md
reports/regression_summary.json
```

## Checks

- build_check：LaTeX/Markdown 是否可构建。
- reference_check：\label、\ref、\cite 是否可解析。
- claim_support_check：每个 strong/comparative claim 是否有 evidence。
- claim_consistency_check：abstract/intro/conclusion 是否漂移。
- reviewer_coverage_check：open issue 是否有正文修改或 response。
- response_alignment_check：response letter 指向真实修改。
- terminology_check：术语定义是否先于使用，符号是否一致。
- source_guard_check：新增 citation 是否有 source card。
- golden_constraint_check：不可改动约束是否被破坏。
- limitation_preservation_check：limitation 是否被删除或弱化。

## Regression report object

```json
{
  "run_id": "run_20260509_001",
  "status": "pass|warn|fail",
  "failed_checks": [],
  "warnings": [],
  "claim_regressions": [],
  "citation_regressions": [],
  "response_regressions": [],
  "recommended_action": "accept|revise_patch|rollback|human_review"
}
```

## Decision rule

- fail：不能合并。
- warn：可以进入人工审核，不能自动关闭 high severity issue。
- pass：可以合并，并写 revision trial。

## Guardrails

- 评估器不直接改文，只报告和建议。
- 对高风险 claim 的“看起来没问题”不能替代人类确认。
- 如果检查依赖缺失状态文件，报告 `insufficient_state`，不要假装通过。
