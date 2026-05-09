# Skill: Meta Skill Optimizer

## Mission

把这套 Paper-HS skills 自身也当成一个 Heuristic System 来维护。它吸收改稿失败、用户反馈、回归失败和重复摩擦，更新 skill 边界、prompt、schemas、tests 和 memory。

这就是“优化 skills 体系的 skill”。它的任务不是让某个 prompt 更华丽，而是降低整套 skill suite 的 coupling complexity。

## When to invoke

- 连续多轮改稿失败。
- 同一类错误重复出现。
- 某个 skill 输出过宽、过窄或和其他 skill 冲突。
- 用户需要把当前经验沉淀成更好的 skill suite。
- Paper-HS 项目结束后做复盘。

## Inputs

- runs/*/revision_trial.json。
- runs/*/regression_report.md。
- reports/dashboard.md。
- user feedback。
- current skills/*.md。
- examples/golden_tasks。

## Outputs

```text
meta/skill_issues.jsonl
meta/skill_trials.jsonl
meta/skill_patch.diff
meta/skill_regression_report.md
meta/skill_changelog.md
meta/golden_skill_tests.jsonl
```

## Skill issue categories

- boundary_confusion：两个 skills 职责重叠。
- missing_state：skill 需要的输入没有被上游生成。
- overbroad_patch：skill 经常产生过大修改。
- hallucination_risk：skill 容易引入未验证事实。
- weak_regression：skill 产物无法被检查。
- memory_pollution：skill 写入过多低质量记忆。
- compression_failure：skill 只增长不压缩。
- user_friction：用户需要重复解释同一约束。
- schema_gap：状态结构表达不了真实问题。

## Meta loop

```text
Observe skill failures
-> Localize to skill boundary / prompt / schema / test / memory
-> Propose minimal skill patch
-> Run golden skill tests
-> Record skill_trial
-> Compress skill rules
```

## Skill issue object

```json
{
  "skill_issue_id": "SI007",
  "observed_failure": "Patch Generator repeatedly strengthened empirical claims without evidence.",
  "affected_skills": ["06_patch_generator", "03_evidence_ledger_builder"],
  "failure_type": "hallucination_risk",
  "evidence": ["run_004/regression_report.md", "run_005/regression_report.md"],
  "proposed_fix": "Add mandatory evidence IDs to Patch Generator output contract.",
  "severity": "high",
  "status": "open"
}
```

## Skill trial object

```json
{
  "skill_trial_id": "ST003",
  "base_version": "v1.0",
  "target_skill_issues": ["SI007"],
  "patch_summary": "Patch Generator now requires evidence IDs for new factual claims.",
  "golden_tests_run": ["no_new_claim_without_evidence", "minimal_patch_scope"],
  "result": "accepted",
  "regressions": [],
  "notes": "Reduced hallucination risk without changing planner behavior."
}
```

## Golden skill tests

A golden skill test is a small synthetic or real paper-editing scenario that the skill suite must handle consistently.

Recommended tests:

1. Reviewer asks for stronger claim but evidence is weak → system downgrades or requests evidence.
2. Related work missing citation → system requests source card before inserting citation.
3. Patch closes R1 but breaks abstract-conclusion consistency → regression catches it.
4. Five accepted patches make intro bloated → Narrative Compressor activates.
5. User states a golden constraint → future patches preserve it.
6. Two reviewer comments conflict → Human Gate activates.
7. Response letter claims a change that patch did not make → Response Aligner catches it.

## Optimization routine

1. **Collect failures.** Read last N runs and identify repeated failure patterns.
2. **Map to system structure.** Decide whether failure lives in a skill boundary, schema, prompt, test, memory, or human gate.
3. **Patch minimally.** Modify one skill or schema at a time when possible.
4. **Run golden tests.** Do not accept a skill change without checking old scenarios.
5. **Record skill trial.** Save why this change was made and what it protects.
6. **Compress.** After several skill patches, merge duplicated rules and simplify instructions.

## Stop rule

If a failure is caused by missing scientific evidence, do not optimize the skill to “write around it.” Add an evidence request, claim downgrade rule, or human gate.

## Guardrails

- 不把用户一次性偏好写成全局规则。
- 不通过增加更多 agent 角色来掩盖边界混乱。
- 不让 meta-skill 只会加规则；它也必须删除、合并、压缩规则。
- skill suite 的目标是更可维护，而不是更复杂。
