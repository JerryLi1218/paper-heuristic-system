# Skill: Revision Planner

## Mission

将 open issues 转化为可执行、低耦合、可回滚的修改计划。该 skill 决定本轮是 local patch、macro-patch、evidence request、claim downgrade、response-only，还是需要 human gate。

## When to invoke

- 已经有 reviewer_issues.jsonl。
- 用户要求“给我修改计划”。
- patch_generator 之前必须经过 planning。
- 多个 issues 互相影响，需要排序。

## Inputs

- reviewer_issues.jsonl。
- claim_graph.json。
- evidence_ledger.json。
- memory/decisions.md。
- memory/failed_directions.md。
- author constraints。

## Outputs

```text
runs/<run_id>/revision_plan.json
reports/revision_plan.md
```

## Patch types

- local_rewrite：局部段落或句子修改。
- structural_reorder：章节结构调整。
- claim_downgrade：降低 claim 强度。
- evidence_integration：加入已有证据。
- citation_integration：加入已验证 source card。
- response_alignment：只改 response letter 或补充 manuscript diff 指向。
- macro_patch：跨章节重构。
- no_patch_needed：解释 why not。
- human_decision_required：需要作者裁决。

## Planning routine

1. 按 severity、coupling complexity、deadline、venue fit 排序 issues。
2. 合并可一起处理的 issues，但限制在同一 claim neighborhood。
3. 对每个候选 patch 写清 hypothesis：为什么这个改动能关闭 issue。
4. 估计 risk：claim risk、evidence risk、citation risk、narrative risk。
5. 选择最小 patch。若最小 patch 无法解决，则声明 macro-patch。
6. 指定 regression checks。

## Revision plan object

```json
{
  "run_id": "run_20260509_001",
  "target_issues": ["R017", "R021"],
  "target_claims": ["C002"],
  "patch_type": "local_rewrite",
  "hypothesis": "A concise contrast paragraph will clarify novelty without strengthening claims.",
  "edits": [
    {"section": "related_work", "operation": "insert_contrast_paragraph"},
    {"section": "method", "operation": "add_boundary_sentence"}
  ],
  "expected_tests": ["claim_support", "citation_integrity", "response_alignment"],
  "risk_level": "medium",
  "human_gate_required": false
}
```

## Guardrails

- 不把所有 open issues 放进同一轮 patch。
- 每个 patch 都必须可撤销。
- 计划必须区分“需要新证据”和“可以用已有证据解释”。
- 高风险 claim 修改必须通过 human gate。
