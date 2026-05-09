# Skill: Memory Manager

## Mission

维护 Paper-HS 的长期记忆：成功策略、失败方向、作者决策、golden constraints、风格偏好、venue 经验。记忆必须可读、可删、可压缩，而不是无限增长。

## When to invoke

- 每轮 patch 接受或拒绝后。
- 出现重复失败方向。
- 论文换 venue 或换核心 framing。
- memory 文件过长或过期。

## Inputs

- revision_trial.json。
- regression_report.md。
- human decision。
- memory/*.md。

## Outputs

```text
memory/decisions.md
memory/failed_directions.md
memory/golden_constraints.md
memory/compression_summaries.md
```

## Memory categories

- accepted_decision：人类确认的方向。
- rejected_direction：尝试过但无效的方向。
- golden_constraint：不能被自动破坏的约束。
- style_preference：作者或 venue 的写作偏好。
- source_policy：引用和事实来源规则。
- regression_lesson：失败检查带来的规则。

## Update routine

1. 从本轮 trial 中提炼一条可复用经验。
2. 判断这条经验是长期规则、短期上下文还是一次性记录。
3. 写入对应 memory 文件。
4. 若 memory 超过阈值，进行 compression：合并重复项、删除过期项、标记失效项。
5. 为高风险记忆加 provenance：来自哪一轮、谁确认。

## Memory entry template

```text
## 2026-05-09 / run_001 / accepted_decision
Context: R2 questioned novelty over X.
Decision: Frame novelty around mechanism, not benchmark score.
Evidence: E004, S012.
Constraint added: Do not claim broad superiority beyond tasks in Table 2.
```

## Guardrails

- 不把一次 reviewer 偏好升级成全局规则。
- 不把失败方向完全遗忘；先记录，再在 compression 中降权。
- 不把未确认的人类意图写成 golden constraint。
