# Skill: Narrative Compressor

## Mission

把多轮局部补丁重新压缩成连贯、简洁、稳定的论文叙事。该 skill 防止论文变成“审稿意见驱动的补丁堆”。

## When to invoke

- 已接受 5 次以上局部 patch。
- introduction、related work 或 experiments 变得重复、臃肿。
- reviewer issue 已关闭，但文本读起来像逐条辩解。
- coupling complexity 持续升高。

## Inputs

- manuscript current。
- revision_trials.jsonl。
- claim_graph.json。
- evidence_ledger.json。
- reviewer_issues.jsonl。
- memory/decisions.md。

## Outputs

```text
runs/<run_id>/compression_patch.diff
reports/narrative_compression_report.md
memory/compression_summaries.md
```

## Compression routine

1. 读取最近若干 accepted patches，抽取它们共同服务的 higher-level purpose。
2. 找到局部重复的 defense sentences、over-explained transitions、reviewer-specific phrases。
3. 将它们合并成更自然的 problem framing、method motivation 或 limitation paragraph。
4. 保持 claim strength 不增强。
5. 保留 evidence 绑定和 response letter 可追踪位置。
6. 运行 regression evaluator。

## Compression modes

- lexical：删除重复词句。
- paragraph：合并 patch-style 段落。
- structural：重排小节顺序。
- rhetorical：把逐条防御改成主动叙事。
- claim-level：重新校准贡献列表。

## Guardrails

- 压缩不能删除 reviewer 已经要求的 clarifications。
- 压缩不能删除 limitation 或 negative result。
- 压缩不能把多个 bounded claims 合成为一个 strong claim。
- 如果 compression 破坏 response alignment，必须更新 response matrix。
