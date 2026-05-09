# Skill: System Science Diagnoser

## Mission

用系统科学视角诊断论文修改过程本身：边界、反馈回路、存量—流量—时滞、层级、网络耦合、杠杆点。它用于找结构性问题，而不是继续调局部措辞。

## When to invoke

- 多轮修改没有明显进展。
- issue closure 低，但文本越来越长。
- 合作者意见反复冲突。
- 论文表面清楚，但核心叙事仍然不稳。
- skill suite 的复杂度失控。

## Inputs

- dashboard metrics。
- revision_trials.jsonl。
- reviewer_issues.jsonl。
- memory files。
- current manuscript outline。

## Outputs

```text
reports/system_diagnosis.md
reports/leverage_points.md
```

## Diagnostic frames

### Boundary

- 这轮修改的系统边界是什么？
- 哪些问题其实属于环境：缺实验、缺数据、venue mismatch、作者未决策？

### Feedback loop

- 反馈是否能被定位到 claim/evidence/section？
- 是否存在“审稿意见 -> 局部加句子 -> 文本更臃肿 -> reviewer 更困惑”的正反馈？

### Stock-flow-delay

- 积累的 stock 是什么：未解决 issues、技术债、记忆污染、引用缺口、作者分歧？
- flow 是什么：patch 速度、review 速度、实验补充速度？
- delay 在哪里：人类确认、实验运行、合作者反馈？

### Hierarchy

- 问题发生在句子、段落、章节、论文叙事、领域定位还是投稿策略层？

### Network coupling

- 哪些 claim 牵动最多 section？
- 哪些 reviewer issues 互相冲突？
- 哪些 evidence 是系统瓶颈？

### Leverage point

- 最有效的干预是改措辞、改信息流、改规则、改目标，还是改 framing？

## Guardrails

- 诊断要落到可执行动作，不停留在概念类比。
- 不把系统科学术语当成装饰；每个术语都要连接到具体论文 artifact。
- 如果真正杠杆点是补实验或降级 claim，应明确指出。
