# Skill: Patch Generator

## Mission

根据 revision_plan 生成最小、可验证、可回滚的稿件修改。该 skill 的产物应是 patch，而不是无边界重写。

## When to invoke

- 已经存在 revision_plan.json。
- 用户要求直接改某个 section。
- reviewer issue 已定位到具体 claim/section。

## Inputs

- revision_plan.json。
- manuscript relevant sections。
- claim_graph.json。
- evidence_ledger.json。
- style_guide.md。
- golden_constraints.md。

## Outputs

```text
runs/<run_id>/patch.diff
runs/<run_id>/before_after.md
runs/<run_id>/patch_rationale.md
```

## Patch discipline

1. 只修改 plan 指定的 section。
2. 每次只服务明确 target issues。
3. 保留原稿中被 evidence 支撑的核心信息。
4. 对新增 claim 标注对应 evidence/source。
5. 对不确定处使用 bracketed request，例如 `[AUTHOR: confirm whether ...]`。
6. 生成 before/after 对照，方便人工审核。

## Allowed operations

- clarify sentence
- split long paragraph
- add topic sentence
- add transition sentence
- narrow claim
- add limitation sentence
- add verified citation
- move paragraph
- delete redundant phrase
- add response pointer

## Forbidden operations

- invent result
- invent citation
- invent theorem
- strengthen claim without evidence
- delete limitation silently
- alter numbers or metrics without source
- change method semantics without author approval

## Output template

```text
# Patch Rationale
Target issues: R017, R021
Target claims: C002
Hypothesis: ...
Risk: medium
Evidence used: E003, S012

# Diff
```diff
...
```

# Before / After
...

# Required regression checks
- claim_support
- citation_integrity
- terminology_consistency
- response_alignment
```

## Guardrails

- 如果修改需要外部事实，先调用 Citation Source Guard。
- 如果修改改变核心 claim，先调用 Human Gate。
- 如果局部修改变得越来越长，停止并转 Narrative Compressor。
