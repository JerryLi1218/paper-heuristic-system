# Paper-Heuristic System Skills v1.0

这是一套用于“已有论文修改迭代”的 Paper-Heuristic System（Paper-HS）技能体系。它把论文从一次性文本产物转化为可观察、可回滚、可测试、可压缩的工程系统。

核心原则：**可迭代的就是可解决的**。但迭代必须留下状态、反馈、测试和记忆；否则只是反复改字句。

## 1. 你什么时候使用这套 skills

适用场景：

- 已有论文需要修改、重投、扩展、压缩、转 venue。
- 有审稿意见、导师意见、合作者意见、rebuttal、camera-ready checklist。
- 论文有多个版本，改动牵一发动全身。
- 你希望每一轮修改都可追踪、可回滚、可复盘，而不是让 LLM 一次性“润色”。

不适合直接全自动处理的场景：

- 需要新增真实实验结果、证明、数据或引用，但系统没有这些来源。
- 作者真实研究意图尚未明确。
- 论文核心贡献尚未定型，只是早期 brainstorming。

## 2. Paper-HS 的最小闭环

```text
Observe        读取论文、审稿意见、作者约束、测试失败
Localize       映射到 claim / evidence / section / citation / response
Plan           选择最小可验证 patch 或 macro-patch
Patch          修改稿件或 response letter
Evaluate       跑 regression checks 和 rubric checks
Record         写 revision_trials.jsonl
Compress       定期压缩叙事、memory 和 skill 规则
```

## 3. 推荐项目结构

```text
paper_hs_project/
  manuscript/                 # 原稿：tex/md/docx 转出的文本
  state/                      # 可机器读取的论文状态
    claim_graph.json
    evidence_ledger.json
    reviewer_issues.jsonl
    source_cards.jsonl
    section_interfaces.json
    terminology.json
  memory/                     # 可读、可删、可压缩的长期记忆
    decisions.md
    failed_directions.md
    golden_constraints.md
    style_guide.md
    compression_summaries.md
  tests/                      # 回归检查配置和 golden cases
    golden_claims.jsonl
    golden_responses.jsonl
  runs/                       # 每轮修改记录
  reports/                    # dashboard、diff、response matrix
  skills/                     # 本 skill suite 的副本或项目特化版
```

## 4. Skill 调用顺序

第一次接入一篇论文：

```text
00_controller
-> 01_ingest_existing_paper
-> 02_claim_graph_extractor
-> 03_evidence_ledger_builder
-> 04_reviewer_issue_mapper
-> 07_regression_evaluator
-> 05_revision_planner
-> 06_patch_generator
-> 07_regression_evaluator
-> 10_memory_manager
-> 09_narrative_compressor
```

有审稿意见时：

```text
04_reviewer_issue_mapper
-> 05_revision_planner
-> 06_patch_generator
-> 08_response_letter_aligner
-> 07_regression_evaluator
-> 10_memory_manager
```

多轮迭代后：

```text
09_narrative_compressor
-> 13_metrics_dashboard
-> 14_meta_skill_optimizer
```

## 5. 快速开始

```bash
python scripts/init_paper_hs.py --out my_paper_hs --title "My Paper"
cp -r /path/to/your/manuscript/* my_paper_hs/manuscript/
python scripts/extract_latex_outline.py --root my_paper_hs/manuscript --out my_paper_hs/state/section_interfaces.json
python scripts/validate_state.py --project my_paper_hs
python scripts/run_regression_checks.py --project my_paper_hs
python scripts/compute_coupling_complexity.py --project my_paper_hs --out my_paper_hs/reports/coupling_complexity.json
```

## 6. 硬约束

1. 不发明实验结果、定理、引用、审稿意见或作者意图。
2. 新增事实性 claim 必须能追到 evidence 或 source card。
3. 高风险 claim、novelty framing、实验解释、conclusion 修改需要 human gate。
4. 每次 patch 后写入 revision_trials.jsonl。
5. 每若干次局部 patch 后进入 compression 阶段。
6. 回归失败时优先回滚或缩小 patch，而不是继续堆补丁。

## 7. 本包内容

```text
skills/      15 个 SKILL.md，可直接复制到 agent/skills 目录
prompts/     控制器、局部修改、评审模拟、claim 抽取、meta 优化 prompts
schemas/     JSON Schema，用于规范状态文件
scripts/     无外部依赖的 Python 辅助脚本
configs/     默认 rubric、risk gate、复杂度权重
examples/    一个最小示例项目
```
