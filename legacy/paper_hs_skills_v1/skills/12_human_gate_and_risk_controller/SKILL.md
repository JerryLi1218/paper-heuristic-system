# Skill: Human Gate and Risk Controller

## Mission

识别需要人类作者确认的修改，并把风险显式化。它控制 Paper-HS 的权限边界。

## When to invoke

- 修改 central claim、novelty framing、experimental conclusion、theorem statement。
- 删除 limitation、negative result、baseline、ablation。
- 引入新外部事实或争议性归因。
- reviewer issues 之间冲突。

## Inputs

- proposed patch。
- claim_graph.json。
- evidence_ledger.json。
- golden_constraints.md。
- reviewer_issues.jsonl。

## Outputs

```text
runs/<run_id>/human_gate_request.md
runs/<run_id>/risk_assessment.json
```

## Risk levels

- low：措辞清晰化，不改变 claim。
- medium：局部重排、引用整合、bounded claim 调整。
- high：核心贡献、证据解释、novelty boundary、实验结论变化。
- critical：可能改变研究事实、作者立场、伦理声明或投稿策略。

## Human gate request template

```text
# Human Gate Required
Run: run_...
Risk: high
Proposed change: ...
Affected claims: C001, C002
Affected evidence: E003
Reason gate is required: ...
Options:
A. Accept patch as written
B. Narrow claim further
C. Reject patch
D. Provide missing evidence
```

## Guardrails

- human gate 不是形式审批；必须说明具体风险。
- 如果缺少证据，选项中必须包含 downgrade 或 evidence request。
- 不能把 critical risk patch 自动合并。
