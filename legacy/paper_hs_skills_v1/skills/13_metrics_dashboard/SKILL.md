# Skill: Metrics Dashboard

## Mission

用可解释指标追踪 Paper-HS 的健康状态：复杂度、反馈吸收效率、回归失败、issue closure、memory 质量、叙事压缩程度。

## When to invoke

- 每轮 patch 后。
- 每个 revision cycle 结束后。
- 准备 rebuttal / resubmission / camera-ready 前。
- meta-skill optimizer 需要判断 skill suite 是否退化。

## Inputs

- claim_graph.json。
- evidence_ledger.json。
- reviewer_issues.jsonl。
- revision_trials.jsonl。
- regression reports。
- memory files。

## Outputs

```text
reports/dashboard.md
reports/coupling_complexity.json
reports/revision_efficiency.csv
```

## Core metrics

```text
open_high_severity_issues
unsupported_claims
overstrong_claims
claim_evidence_density
cross_section_dependency_count
reviewer_conflict_count
regression_failure_rate
accepted_patch_rate
average_patch_scope
memory_growth_rate
compression_interval
response_alignment_coverage
```

## Coupling complexity heuristic

```text
score =
  1.5 * high_risk_claim_count
+ 1.2 * cross_section_dependency_count
+ 1.2 * reviewer_conflict_count
+ 1.0 * unsupported_claim_count
+ 0.8 * citation_gap_count
+ 0.8 * notation_alias_count
+ 0.7 * unresolved_regression_count
+ 0.5 * active_branch_count
- 1.0 * stable_interface_count
- 1.0 * passing_regression_suite_count
- 0.8 * compressed_memory_quality
```

## Interpretation

- complexity rising + issue closure low：定位失败，回到 Reviewer Issue Mapper。
- complexity rising + issue closure high：需要 Narrative Compressor。
- regression failure high：patch generator 过宽或 tests 不稳定。
- unsupported claims high：Evidence Ledger 或 Claim Graph 需要重建。
- memory growth high：Memory Manager 需要 compression。

## Guardrails

- 指标辅助决策，不替代作者判断。
- 不追求低复杂度本身；高质量复杂系统可以接受，但必须有模块边界和回归测试。
