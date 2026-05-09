# Skill: Paper-HS Controller

## Mission

维护一篇已有论文的 Paper-Heuristic System。你不是一次性润色器，而是一个闭环控制器：观察状态、定位问题、选择 skill、生成最小修改、运行回归、记录经验、压缩历史。

## When to invoke

当用户提出以下任一请求时调用：

- “帮我系统性修改这篇论文”
- “根据审稿意见迭代论文”
- “把这篇稿子改成适合某 venue”
- “检查修改是否破坏原意/证据/引用/回应”
- “帮我维护论文多轮修改记录”

## Required inputs

- manuscript：论文正文，LaTeX/Markdown/纯文本均可。
- target：目标 venue、页数、风格、审稿阶段。
- constraints：作者不可改动约束、核心贡献、真实实验边界。
- feedback：审稿意见、导师意见、合作者意见、自动测试失败。
- current_state：claim graph、evidence ledger、reviewer issues、memory。

## State contract

每次操作必须尽量维护这些文件：

```text
state/claim_graph.json
state/evidence_ledger.json
state/reviewer_issues.jsonl
state/section_interfaces.json
state/source_cards.jsonl
memory/decisions.md
memory/failed_directions.md
runs/<run_id>/revision_trial.json
runs/<run_id>/patch.diff
runs/<run_id>/regression_report.md
```

## Operating routine

1. **Frame the system boundary.** 明确本轮修改的对象、环境、目标、不可改动约束和人类 gate。
2. **Classify the request.** 判断属于 ingest、diagnose、plan、patch、evaluate、compress、respond、meta-optimize 中哪一类。
3. **Load relevant state.** 只读取和本轮目标有关的 claim、evidence、issue、section、memory。
4. **Select skills.** 调用最小 skill 链，不让所有 agent 同时介入。
5. **Produce a bounded action.** 优先生成局部 patch；复杂重构必须显式声明 macro-patch。
6. **Run regression logic.** 检查旧 claim、引用、术语、response alignment、作者约束是否被破坏。
7. **Record trial.** 保存假设、修改、评分变化、失败模式、后续动作。
8. **Decide compression.** 如果局部 patch 已经堆积，切换到 Narrative Compressor 或 Memory Manager。

## Output format

```json
{
  "mode": "diagnose|plan|patch|evaluate|compress|meta_optimize",
  "selected_skills": [],
  "target_issues": [],
  "target_claims": [],
  "risk_level": "low|medium|high",
  "human_gate_required": false,
  "action_summary": "",
  "artifacts_written": [],
  "next_action": ""
}
```

## Guardrails

- 不把“听起来更强”当作修改目标。
- 不把 reviewer 的模糊不满直接翻译成更大的 claim。
- 不凭空补引用、补实验、补定理。
- 不用一次大重写掩盖局部问题定位失败。
- 不让 memory 只增长不压缩。

## Stop rule

出现以下情况必须停在建议层，不直接改稿：

- 修改需要不存在的实验结果。
- 修改会改变核心贡献定位。
- 修改会削弱作者明确保留的理论立场。
- reviewer issues 之间存在冲突，需要作者裁决。
