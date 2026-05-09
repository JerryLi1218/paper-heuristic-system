# Paper Heuristic System

> 可迭代的就是可解决的。前提是每一轮迭代都留下状态、反馈、回归检查和可压缩的记忆。

**Paper Heuristic System（Paper-HS）** 是一套面向已有论文修改、重投、rebuttal、camera-ready、related work 与引用核验的 agent skill + 本地 CLI 工程模板。它把论文从一次性文本产物转成一个可维护系统：

```text
manuscript
+ claim graph
+ evidence ledger
+ reviewer issue graph
+ citation/source cards
+ novelty landscape report
+ regression reports
+ revision trials
+ memory
+ meta-skill optimizer
```

## 核心能力

1. **即插即用总 Skill**：复制 `.agents/skills/paper_heuristic_system/` 到任意论文项目即可使用；仓库也包含 `.codex-plugin/plugin.json` 与标准 `skills/` 目录，便于按 plugin 形态传播。
2. **论文项目隔离**：每篇论文拥有自己的 `paper_hs/state`、`paper_hs/memory`、`paper_hs/runs` 与本地 skill 副本，避免不同稿件互相污染。
3. **可回归修改闭环**：每次修改先定位 claim / evidence / reviewer issue / citation，再生成最小 patch，随后运行 regression checks 并记录 trial。
4. **引用核验**：检查 `.tex` citation key、`.bib` 条目、DOI/title/year/author 一致性、重复 DOI、缺失引用和 source card。
5. **新颖性与投稿风险图谱**：用 OpenAlex / Crossref / Semantic Scholar / arXiv 元数据检索近邻工作，输出 prior-art map、novelty risk、危险说法和安全改写建议。
6. **Meta Skill Optimizer**：把 skills 自身也作为 Heuristic System 维护，把反复失败转化为 skill patch、schema patch 或 golden tests。

## 快速开始

```bash
git clone https://github.com/JerryLi1218/paper-heuristic-system.git
cd paper-heuristic-system
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

初始化一篇论文：

```bash
paper-hs init \
  --project ./workspace/my-paper \
  --title "My Paper" \
  --venue "ICLR" \
  --source /path/to/my/paper \
  --install-skill
```

进入项目并打开 Codex：

```bash
cd ./workspace/my-paper
codex
```

给 Codex 的第一条指令：

```text
Use the paper_heuristic_system skill. Ingest this paper, build the claim graph and evidence ledger, then run citation verification before proposing any revision.
```

## 引用与新颖性核验

离线核验：

```bash
paper-hs source-cards --project ./workspace/my-paper
paper-hs cite-check --project ./workspace/my-paper
paper-hs novelty-check --project ./workspace/my-paper --query "一句话描述核心 idea"
```

联网核验：

```bash
paper-hs cite-check --project ./workspace/my-paper --online --mailto you@example.com
paper-hs novelty-check --project ./workspace/my-paper --online --query "一句话描述核心 idea" --mailto you@example.com
```

`source-cards` 会先根据本地 `.bib` 生成保守的 source card；它不会假装知道文献支持了哪句话，只为后续核验建立可追踪入口。

这套功能专门处理几类常见问题：

```text
idea 是否真的够新？
有没有近似工作已经做过？
related work 是否漏掉关键近邻？
“novel / first / SOTA / solves” 这类说法是否过强？
正文 citation key 对了，但 .bib 的 DOI/title/year/author 是否写错？
```

## 项目隔离原则

每篇论文都应该是一个独立系统：

```text
paper-a/
  .agents/skills/paper_heuristic_system/
  paper_hs/

paper-b/
  .agents/skills/paper_heuristic_system/
  paper_hs/
```

可以共享 repo、模板、schema、CLI 和总 skill；不要共享 claim graph、evidence ledger、reviewer issues、memory、failed directions、runs 或 response matrix。

## 重要边界

Paper-HS 可以帮助发现 prior art、核验引用、降低说法风险，但不能数学式证明 idea 一定新颖，也不能替代作者对真实贡献的判断。系统必须停止在建议层，而不是编造实验、引用、定理、审稿意图或作者意图。
