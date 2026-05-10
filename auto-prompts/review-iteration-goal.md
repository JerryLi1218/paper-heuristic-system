# Review-Iteration `/goal` Prompt

Use this prompt in Codex when a Paper-HS project already has a manuscript and a file containing scores, rubric feedback, reviewer comments, or detailed revision advice.

The prompt is intentionally two-stage. It first forces Codex to decompose the feedback and produce a human-gate review document. Only after the author confirms those human-gate decisions should the agent enter unattended Paper-HS iteration.

Replace the placeholder values before running it.

```text
/goal

你现在运行在一个 Paper-HS 项目中。请使用本项目的 paper_heuristic_system skill 和现有 Paper-HS 状态文件，对照评分表与修改意见，启动一次长任务式论文迭代。

输入材料：
- 论文项目根目录：<PAPER_HS_PROJECT_ROOT>
- 评分及修改意见文件：<SCORE_AND_REVIEW_FILE>
- 目标稿件目录或主 tex 文件：<MANUSCRIPT_PATH>
- 目标会议/期刊/评分标准：<VENUE_OR_RUBRIC>
- 用户额外约束：<AUTHOR_CONSTRAINTS>

核心目标：
把评分及修改意见转化为一个可执行、可追踪、可回归检查的 Paper-HS 修改任务集合。先完成需要人工确认的方向筛选；用户确认后，进入无人值守迭代，持续修改、验证、记录，直到所有可处理意见都被关闭或明确标记为需要作者提供新证据。

阶段 1：解析评分与修改意见
1. 阅读评分表、审稿意见、rubric、作者约束、现有 manuscript、paper_hs/state、paper_hs/memory、paper_hs/reports。
2. 将修改意见拆解为多粒度 issues：
   - macro_issue：影响论文主线、贡献定位、整体结构、实验充分性的大问题；
   - section_issue：落到具体章节、图表、related work、methods、experiments、limitations 的问题；
   - claim_issue：落到具体 claim、evidence、citation、wording strength 的问题；
   - mechanical_issue：格式、语言、引用、术语一致性、可读性等局部问题。
3. 为每个 issue 生成稳定 ID，并写入或更新：
   - paper_hs/state/reviewer_issues.jsonl
   - paper_hs/reports/review_issue_decomposition.md

阶段 2：生成人工核验文档并暂停
生成一份必须由用户人工确认的文档：

paper_hs/reports/human_gate_review.md

文档必须包含：
1. 需要人工确认的方向列表。
2. 每个方向对应的 review issue IDs。
3. 为什么需要人工确认。
4. 可选决策项，例如：
   - 是否接受某个审稿人的 framing；
   - 是否改变中心贡献；
   - 是否新增实验或只保守改写；
   - 是否降级 novelty / SOTA / first-to-do 类表述；
   - 冲突意见之间选择哪一条作为主导。
5. 每个方向给出推荐选择，但清楚标注哪些只是 agent 判断。

完成该文档后必须暂停，向用户汇报：
- issue 拆解完成；
- human_gate_review.md 的路径；
- 需要用户逐项确认的内容；
- 在用户回复前不得进入正文修改。

阶段 3：处理用户人工确认
收到用户确认后：
1. 将用户确认映射回 reviewer_issues.jsonl 中的 issue IDs。
2. 如果某个人工确认方向无法映射到现有 issue，必须继续询问用户，直到每个必须人工确认方向都满足以下之一：
   - 已映射到现有 issue；
   - 已创建新的 issue；
   - 已明确标记为 out_of_scope；
   - 已标记为 blocked_by_missing_evidence。
3. 写入：
   - paper_hs/reports/human_gate_resolution.md
   - paper_hs/memory/author_constraints.md
   - 必要时更新 reviewer_issues.jsonl

只有所有 human-gate 方向都关闭后，才能进入无人值守模式。

阶段 4：无人值守 Paper-HS 迭代
进入无人值守后，持续执行 Paper-HS loop：

Observe -> Localize -> Plan -> Patch -> Evaluate -> Record -> Compress

对每个 issue：
1. Observe：读取相关章节、claim graph、evidence ledger、source cards、citation reports、novelty reports。
2. Localize：定位到具体 claims、sections、figures、tables、citations、equations 或 response-letter rows。
3. Plan：给出最小可验证 patch。大型结构变化标记为 macro-patch。
4. Patch：修改稿件和必要的 Paper-HS state。
5. Evaluate：运行或模拟回归检查：
   - claim support
   - citation integrity
   - novelty wording safety
   - terminology consistency
   - reviewer coverage
   - abstract/conclusion consistency
   - figure/table caption consistency
6. Record：为每轮写入 paper_hs/runs/<run_id>/：
   - patch.diff
   - regression_report.md
   - revision_trial.json
7. Compress：若多轮 patch 造成文本堆叠，要恢复成连贯论文叙述。

阶段 5：引用与新颖性保护
凡是涉及 related work、novelty、SOTA、first、no prior work、generalizes、solves、comprehensive 等表述，必须运行或更新：
- paper-hs source-cards --project .
- paper-hs cite-check --project .
- paper-hs novelty-check --project . --query "<central idea>"

如果在线检索不可用，生成离线报告，并把未完成的在线验证标为 unresolved，而不是假装已经验证。

阶段 6：停止条件
无人值守任务一直运行，直到满足以下条件之一：
1. 所有 reviewer issues 均为 resolved / accepted_with_limits / out_of_scope / blocked_by_missing_evidence。
2. 存在必须新增实验、作者立场、真实数据或外部事实才能继续的问题。
3. 回归检查发现当前修改会破坏中心 claim 或证据链，需要作者重新决策。
4. 论文成功完成一轮全量修改，并生成最终报告。

最终交付物：
- 修改后的 manuscript；
- paper_hs/state/reviewer_issues.jsonl；
- paper_hs/reports/review_issue_decomposition.md；
- paper_hs/reports/human_gate_review.md；
- paper_hs/reports/human_gate_resolution.md；
- paper_hs/reports/final_revision_report.md；
- paper_hs/reports/response_letter_draft.md；
- paper_hs/reports/regression_summary.md；
- 所有 paper_hs/runs/<run_id>/ 记录。

最终报告必须说明：
1. 每条评分/修改意见如何被处理；
2. 哪些改动进入正文；
3. 哪些 claim 被降级、加强、删除或保留；
4. 哪些 citation / novelty / evidence 风险仍然存在；
5. 哪些问题需要作者补充实验、数据或立场判断。

重要边界：
不要编造实验结果、引用、DOI、页码、审稿人意图或作者意图。不要为了提高评分而强化没有证据支持的 claim。所有无法验证的内容必须保守处理并记录。
```
