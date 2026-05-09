# Skill: Reviewer Issue Mapper

## Mission

把审稿意见、导师意见、合作者意见转成可追踪、可排序、可关闭的 issue graph。该 skill 让“模糊反馈”变成系统状态。

## When to invoke

- 收到 review / meta-review / rebuttal questions。
- 导师给出长段修改意见。
- 多位合作者意见互相冲突。
- 需要生成 response matrix。

## Inputs

- feedback text。
- claim_graph.json。
- evidence_ledger.json。
- section_interfaces.json。

## Outputs

```text
state/reviewer_issues.jsonl
reports/reviewer_issue_matrix.md
reports/conflict_map.md
```

## Issue categories

- novelty_unclear
- evidence_insufficient
- claim_overreach
- missing_baseline
- missing_ablation
- unclear_method
- notation_confusing
- related_work_gap
- evaluation_protocol_gap
- writing_clarity
- limitation_missing
- reproducibility_gap
- ethics_or_safety_gap
- venue_fit

## Issue object

```json
{
  "issue_id": "R017",
  "source": "Reviewer 2",
  "raw_text": "The novelty over X is unclear.",
  "category": "novelty_unclear",
  "severity": "high",
  "mapped_claims": ["C002", "C005"],
  "mapped_evidence": ["E009"],
  "mapped_sections": ["related_work", "method"],
  "required_action": "clarify novelty boundary and add contrast table",
  "risk": "medium",
  "status": "open",
  "conflicts_with": [],
  "success_criteria": ["response cites changed section", "claim strength unchanged or narrowed"]
}
```

## Procedure

1. 分句读取反馈，拆成 atomic issues。
2. 每个 issue 绑定 claim、evidence、section。
3. 判断 severity：blocking、high、medium、low。
4. 判断 action type：clarify、add evidence、downgrade claim、add citation、add experiment request、reframe、compress。
5. 建 conflict edges：例如 R1 要增强 claim，R2 要降低 claim。
6. 生成 reviewer_issue_matrix。

## Closing rule

一个 issue 只有同时满足以下条件才可以标记为 closed：

- 正文中有对应修改或有明确不修改理由。
- response letter 有逐点回应。
- claim/evidence/section mapping 仍然一致。
- regression evaluator 没有发现新破坏。

## Guardrails

- 不把 reviewer 的建议自动当作必须照做；可以标记为 `decline_with_reason`。
- 不合并语义不同的 issue，只因为它们来自同一段评论。
- 不把一个大 issue 伪装成一个小措辞修改。
