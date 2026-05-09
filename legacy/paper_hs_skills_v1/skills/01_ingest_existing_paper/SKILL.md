# Skill: Ingest Existing Paper

## Mission

把一篇已有论文转成可迭代维护的 Paper-HS 初始状态。该 skill 负责建立边界、章节地图、作者约束、初始风险清单和 artifact inventory。

## When to invoke

- 第一次把论文接入 Paper-HS。
- 论文换 venue、换版本、换主要贡献叙事。
- 项目状态混乱，需要重新建立 baseline。

## Inputs

- manuscript files：paper.tex、sections/*.tex、paper.md 或纯文本。
- metadata：title、authors、target venue、deadline、page budget。
- constraints：不可修改内容、必须保留贡献、真实实验边界。

## Outputs

```text
state/paper_inventory.json
state/section_interfaces.json
memory/golden_constraints.md
memory/style_guide.md
reports/ingestion_report.md
```

## Procedure

1. 列出所有正文、图表、表格、公式、附录、bib、supplement 文件。
2. 识别章节结构：section、subsection、paragraph-level role。
3. 标记每一章的输入和输出：它依赖什么前提，承诺交付什么。
4. 抽取显式贡献列表、实验设置、数据集、baseline、metric。
5. 抽取作者约束：不可降级 claim、不可删除实验、必须保留术语。
6. 标记高风险区域：abstract、contribution paragraph、main theorem、main table、limitation。
7. 生成 ingestion report，说明哪些状态文件还缺失。

## Section interface template

```json
{
  "section_id": "S003",
  "title": "Method",
  "role": "define the proposed method and justify design choices",
  "inputs": ["problem formulation", "notation"],
  "outputs": ["algorithm definition", "complexity claim"],
  "depends_on": ["S002"],
  "feeds_into": ["S004", "S005"],
  "risk": "medium"
}
```

## Quality checks

- 每一章都应该有 role。
- abstract、intro、conclusion 必须能互相映射。
- contribution list 不应超过论文真正能支撑的证据。
- 任何“必须保留”的作者约束都要写入 golden_constraints.md。
