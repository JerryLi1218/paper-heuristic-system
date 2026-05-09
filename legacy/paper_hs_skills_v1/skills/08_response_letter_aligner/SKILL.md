# Skill: Response Letter Aligner

## Mission

生成或检查 response letter，确保每条回应都与 reviewer issue、manuscript diff、claim/evidence 状态对齐。它把 rebuttal 从文学修辞变成可追踪的响应矩阵。

## When to invoke

- rebuttal / revision response / camera-ready response。
- 审稿意见已经映射成 reviewer_issues.jsonl。
- 正文已有 patch，需要生成逐点回应。
- 用户担心 response letter 和正文不一致。

## Inputs

- reviewer_issues.jsonl。
- patch.diff。
- manuscript after。
- claim_graph.json。
- evidence_ledger.json。
- target venue tone。

## Outputs

```text
reports/response_matrix.md
response_letter.md
runs/<run_id>/response_alignment_report.md
```

## Response matrix columns

```text
Issue ID | Reviewer | Concern | Manuscript Change | Location | Response Summary | Status | Risk
```

## Response style

- 先承认有效问题。
- 明确说明做了什么修改。
- 给出章节、段落、表格、附录位置。
- 如果不同意 reviewer，给出尊重但清晰的理由。
- 不夸大修改幅度。
- 不声称完成了没有完成的实验。

## Alignment checks

- response 中提到的修改必须能在 patch.diff 中找到。
- response 中提到的 claim 必须存在于 claim_graph。
- response 中提到的证据必须存在于 evidence_ledger。
- 未修改的问题必须标记为 `decline_with_reason` 或 `future_work`，不能伪装成已解决。

## Guardrails

- 不把 response letter 写得比正文更强。
- 不承诺 camera-ready 中不存在的补实验。
- 不隐藏 reviewer conflict；冲突应在 response 中审慎处理。
