# 新项目初始化与 Matt Skills 接入

新建业务仓库时先完成平台绑定，再接入 Agent；已有项目只补缺项。`setup-matt-pocock-skills` 提供 Other tracker 扩展点，将云效映射放进项目的 `docs/agents/issue-tracker.md`，保留 Matt Skills 的通用工程方法。

## 项目与仓库的边界

ProjeX 项目按产品、团队或共同交付目标组织需求；Codeup 仓库按代码、权限和发布边界组织。Matt Skills 不要求两者一对一。

- 独立工具或单仓库产品：一个项目对应一个仓库，配置最少。
- 同一产品的前端、后端等多个仓库：默认共用一个项目，在工作项中明确涉及的仓库与交付范围。
- 负责人、权限、工作流或交付节奏独立：拆成不同项目，需要统一规划时使用项目集；不因新增一个仓库机械新建项目。

规格与切片按可验证的业务行为组织，不为匹配仓库数量把纵向切片强拆为前端票、后端票。同一工作项可关联多个 MR；每个仓库的 tracker 只保存自身绑定、共同规则的权威入口和必要的关联仓库，不复制业务进度。

当前 Matt `implement-spec` 面向一个仓库的一条集成分支。跨仓库规格需要协调者分别安排各仓库的实现范围、集成分支和 MR，并在 ProjeX 汇总所需交付及兼容顺序；Git 分支和 worktree 不能跨仓库共享，也不能宣称一次原版调用会自动编排所有仓库。任一必需仓库未满足验收，父需求保留未完成。

## 平台初始化

按已授权范围执行以下步骤；复用已核对的项目、服务连接和规则，创建前查重。只记录真实资源与尚缺配置，不把本指引转成第二套本地进度台账。实际命令参数按 CLI `--help` 或官方 API 查明；没有已验证写接口的管理配置使用平台页面，不猜接口。

1. **环境与身份**：按 [访问指引](access.md) 安装或检查 CLI、插件与本机凭据入口，验证身份和目标组织。独立验证 Git 读写认证；API 可用不代表能够推送。已有入口正常时不重建 PAT。
2. **ProjeX 项目**：按上面的边界复用或创建项目，核对项目模板、成员、需求/任务/缺陷类型、必填字段与合法状态流转。按 [状态映射](projex.md#matt-执行阶段与业务状态)确定依赖解除和关闭的标准，按 [关系指引](projex.md#父子关联与依赖)逐一核对需要的源/目标类型组合；管理员补齐后重新验证，不沿用旧的不可用结论。只补实际需要的就绪标记。组织级类型关系或共享模板的修改需计入本次范围，不能因初始化一个项目就改动其他项目。
3. **Codeup 仓库与追踪**：核对代码库组、可见性、成员权限、真实 remote 和目标分支；新仓库完成必要初始提交后再创建有差异的 MR。在 ProjeX 项目服务中启用并关联对应代码库、流水线（界面可用时）。项目级关联用于入口和资源聚合，仍需为具体 MR 设置 `workItemIds` 并回读。项目成员也须拥有对应代码库/流水线的访问权限。
4. **CI 与合并保护**：按 [交付指引](delivery.md) 建立只测试的 Flow 流水线，使用真实 Codeup 服务连接，固定支持的运行环境。核对代码源的 MR 新建/更新触发和目标分支过滤，将对应流水线设为保护分支的必需检查，验证结果对应 MR 当前提交。设置目标分支的推送限制和必要评审；普通推送不能绕开要求的 MR。可见的成功 CI 不等于强制门禁已启用。部署阶段按项目需要另配，Testhub 仅在需要测试计划或人工验收管理时接入。
5. **按需联动**：按 [自动化与事件](automation.md) 配置 Codeup → ProjeX 事件和少量状态规则。采用 Agent 手动推进也能开始开发；未配置联动时写明责任主体。ProjeX → 外部 Agent 的 Webhook 另行按需求启用，不作为建仓前置条件。多个仓库逐一核对事件订阅，不能只给第一个仓库配置。
6. **Agent 接入与验收**：填写 [项目绑定模板](../assets/issue-tracker.md)，按下节接入 Matt Skills。用获准的测试工作项/分支验证工作项读取、原生 MR 关联、对应 SHA 的 CI、状态映射和已启用的联动；合并及状态写入须在授权范围内。负向验证失败 CI、旧 SHA 成功、未完成的其他仓库都不能被当成整体交付通过。只报告实际通过的能力；必需配置缺失时列明负责人和操作入口，不宣称该部分完成。未选用的可选服务不阻塞基础开发。

## 接入 Matt Skills

按用户调用的 setup Skill 探索真实仓库，确定 remote、现有指令文件、已有文档、triage 安装情况及 monorepo 信号。空临时目录只生成模板，不冒充已初始化业务项目。

用户已指定 ProjeX 时，tracker 选择已确定，不再询问 GitHub/本地 Markdown。读取 [issue-tracker 模板](../assets/issue-tracker.md)，补入已验证资源，展示待写文档和指令块供审阅，再应用。

遵循 setup 的文件选择：已有 `CLAUDE.md` 就编辑它，否则编辑已有 `AGENTS.md`；都没有时询问用户创建哪个。已有共享/导入机制时，更新被共享的规范文件，保留引用入口。已有 `## Agent skills` 原位更新，不覆盖其他约定；该标题是 setup 识别配置块的依据，保留英文，其下子标题与 tracker 文档标题用中文。

```markdown
## Agent skills

### 工作项追踪

需求、缺陷和任务以 ProjeX 为准，代码评审使用 Codeup。追踪工作项、创建或评审 MR、
合并分支及同步上游前，读取 `docs/agents/issue-tracker.md` 并加载 `codeup` Skill，
合并策略按其交付指引执行。

### 领域文档

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
| implement-spec | 按 [执行阶段映射](projex.md#matt-执行阶段与业务状态)计算 frontier；各仓库维护自己的集成分支、MR 和证据 |
| wayfinder | 需求作 map、任务子项作决策票；认领用状态而非负责人，见 [Wayfinder 映射](projex.md#wayfinder-映射) |
| triage（若安装） | 按项目的分诊映射读取和更新，不调用 gh label |
| pr / code-review | 内容遵循当前 Skill、用户和项目约定，MR 模板仅在缺少约定时参考；提交后缀中的展示编号按 tracker 的 fetch 章节读取；独立双轴审阅与平台审批分别核验 |
| domain-modeling | 沿用 glossary/ADR，不把跟踪平台差异混入业务术语 |

Matt Skills 决定设计、拆票、实现与审阅方法；本 Skill 负责云效对象、调用及结果核验；tracker 保存项目资源与状态映射；平台保存业务进度；设备部署文档保存 CLI 与凭据入口。正文、评论、MR 的内容和结构沿用当前 Skill、用户与项目约定，本 Skill 只处理平台格式兼容。遇到具体 Skill 硬编码 `gh`，先检查其可配置点；必要时对该 Skill 做最小改动，不全局替换系统 `gh`。

## 双 Agent 使用

同一完整 Skill 目录可安装到 Claude Code 的用户/项目 Skills 目录，以及 Codex 当前支持的 Skills 目录。保持同一内容版本，不能只复制 `SKILL.md` 而漏掉 references、assets、scripts 或 agents 元数据。

setup 只编辑一个已有指令文件，不能假定另一个 Agent 会自动读取它。检查项目当前指令共享/导入机制；如果另一端没有读取入口，展示最小引用改动供用户确认，再补齐。不要擅自创建第二套冲突规范。

各 Agent 首次接入分别验证其实际执行环境能读取同一 tracker、加载完整 Skill 并访问绑定资源；安装文件一致不代表两种 Agent 已独立通过业务全流程。

## 来源

- [ProjeX 项目关联代码库与流水线](https://help.aliyun.com/zh/yunxiao/product-overview/2023-1)
- [MR 流水线合并检查](https://help.aliyun.com/zh/yunxiao/user-guide/extending-code-detection-through-pipelining)
- Matt Skills 适配基线：`mattpocock/skills` 于 2026-10-10 安装的版本，tracker 章节以其 `setup-matt-pocock-skills/issue-tracker-github.md` 为准；上游更新后重新核对。
- 关系、状态与 Webhook 的官方来源见 [ProjeX](projex.md#来源) 和 [自动化](automation.md#来源)；平台设置于 2026-10-11 核对，仍需按目标租户权限实测。
