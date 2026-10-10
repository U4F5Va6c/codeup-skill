# 接入 Matt Pocock 工程 Skills

`setup-matt-pocock-skills` 已提供 Other tracker 扩展点。不修改其通用技能源文件，将云效约定放进每个项目的 `docs/agents/issue-tracker.md` 即可。

## 初始化

按用户调用的 setup Skill 探索真实仓库，确定 remote、现有指令文件、已有文档、triage 安装情况及 monorepo 信号。空临时目录只生成模板，不冒充已初始化业务项目。

用户已指定 ProjeX 时，tracker 选择已确定，不再询问 GitHub/本地 Markdown。读取 [issue-tracker 模板](../assets/issue-tracker.md)，补入已验证资源，展示待写文档和指令块供审阅，再应用。

遵循 setup 的文件选择：已有 `CLAUDE.md` 就编辑它，否则编辑已有 `AGENTS.md`；都没有时询问用户创建哪个。已有共享/导入机制时，更新被共享的规范文件，保留引用入口。已有 `## Agent skills` 原位更新，不覆盖其他约定。

```markdown
## Agent skills

### Issue tracker

需求、缺陷和任务以 ProjeX 为准，代码评审使用 Codeup。追踪工作项、创建或评审 MR、
合并分支及同步上游前，读取 `docs/agents/issue-tracker.md` 并加载 `codeup` Skill，
合并策略按其交付指引执行。

### Domain docs

采用 single-context；探索相关领域前读取 `docs/agents/domain.md`。
```

单上下文使用 [domain 模板](../assets/domain.md)。发现真实 monorepo 且用户选择多上下文时再调整；不要先创建空 glossary 或 ADR。

合并规则集中维护在 [交付指引](delivery.md#分支角色与默认合并策略)；项目指令只保留加载入口，项目有不同策略时在 tracker 文档写明例外。无需将默认策略复制到全局或项目级 `AGENTS.md` / `CLAUDE.md`；双 Agent 共用一份规范，另一入口沿用项目的引用机制。

## Triage 条件

未安装 `triage`：按 setup 跳过 Section B，不生成 `triage-labels.md` 或对应指令块，不创建五个线上标签。`to-spec` / `to-tickets` 仍可能要求 ready-for-agent；在 tracker 文档里单独约定就绪标记如何落地。

已安装 `triage`：按 setup 只问是否保留五个默认名称，接受已有公司命名映射。确认 ProjeX 实际标签 ID 和可用写接口后再写映射；若只有自定义字段可表达，需要明确记录。标签不替代业务状态。

## 各 Skill 消费方式

| Skill | ProjeX 落地 |
|---|---|
| to-spec | 需求工作项承载规格，保留其原有测试边界确认流程 |
| to-tickets | 审阅后的纵向切片作为任务/子项，保留真实依赖，不自动关闭父项 |
| triage（若安装） | 按项目的分诊映射读取和更新，不调用 gh label |
| pr / review | 按项目 MR 模板组织说明，调用 Codeup 工具 |
| domain-modeling | 沿用 glossary/ADR，不把跟踪平台差异混入业务术语 |

这些 Skill 产生什么内容由各自规则决定，tracker 文档和本 Skill 决定内容如何发布到云效。遇到具体 Skill 硬编码 `gh`，先检查其可配置点；必要时对该 Skill 做最小改动，不全局替换系统 `gh`。

## 双 Agent 使用

同一完整 Skill 目录可安装到 Claude Code 的用户/项目 Skills 目录，以及 Codex 当前支持的 Skills 目录。保持同一内容版本，不能只复制 `SKILL.md` 而漏掉 references/assets。

setup 只编辑一个已有指令文件，不能假定另一个 Agent 会自动读取它。检查项目当前指令共享/导入机制；如果另一端没有读取入口，展示最小引用改动供用户确认，再补齐。不要擅自创建第二套冲突规范。

首次业务验收以一个明确工作项和测试分支跑通：读取 → 本地测试 → 推送 → MR → 原生关联回读 → CI SHA 核对。只有被授权时才执行合并、评论或状态更新。
