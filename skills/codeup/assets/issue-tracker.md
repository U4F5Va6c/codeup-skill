# 工作项追踪：ProjeX + Codeup

这是接入模板。填入并核对本项目资源后才能作为已生效配置；不在此保存令牌。

## 项目绑定

| 项目属性 | 待核对值 |
|---|---|
| 云效部署 | 中心版 |
| API 接入点 | https://openapi-rdc.aliyuncs.com |
| 各执行环境的认证指引 | 待引用机器部署文档；记录入口与凭据引用，不保存令牌 |
| organizationId | 待从组织确认 |
| ProjeX projectId / spaceId | 待从项目确认 |
| ProjeX 项目 URL | 待从真实页面确认 |
| 项目边界与协作范围 | 待说明产品/交付目标；单仓库或关联多个仓库，跨项目协作仅记录权威入口 |
| Codeup 仓库 ID、完整路径、URL、Git remote | 待逐一确认；支持多个仓库 |
| 默认目标分支 | 从各仓库读取 |
| 合并策略例外 | 无则使用 codeup Skill 默认策略；存在项目策略或平台限制时写明差异 |
| 需求 / 缺陷 / 任务的类型 ID | 从当前项目元数据读取 |
| 必填字段和默认负责人 | 从项目约定及字段配置确认 |
| 就绪标记 | 待选择已有原生标签、既有字段，或明确约定的正文 Agent readiness 字段 |
| wayfinder 标签 | 使用 wayfinder 时记录 `wayfinder:map` 与四种 `wayfinder:<type>` 的标签 ID；未使用可留空 |
| 关系映射 | 分别记录父子、ASSOCIATED、DEPEND_ON 允许的源/目标类型组合；变更后重新查询并验证方向，记录不可用时的明确回退方式 |
| 业务状态与关闭标准 | 按各工作项类型填写实际状态 ID、合法流转、任务验收范围和父需求验收规则 |
| 依赖解除条件 | 待约定可供后继使用的集成代码/制品/部署证据；与任务关闭分别判断 |
| CI 流水线 / 必需检查 | 待绑定各仓库及分支规则 |
| 状态推进负责方 | 待逐项约定 Agent、自动化或人工负责的转换；自动化记录规则管理入口/ID、范围与触发事实 |
| Codeup → ProjeX 事件接入 | 逐仓库确认已配置、未配置或待验证；仅记录非敏感 Hook/规则 ID 与凭据引用 |
| 外部 Agent 事件唤醒 | 未启用即可；按需记录接收端管理入口、去重/领取方式及授权范围，不保存 Secret 或带密钥的触发 URL |
| 部署范围 | 待记录环境与本项目授权规则 |

## 真相来源与操作

ProjeX 保存需求、缺陷、任务、关系和验收状态；Codeup 保存代码与合并请求；Flow 保存实际流水线执行。规格内容沿用当前 Matt Skill 的发布位置，仓库文档可保存被引用的设计与领域决策，避免两处人工维护相同内容或进度。本文只保存项目配置与映射，设备部署文档负责安装和凭据入口。

进行需求追踪、拆票、评审发布、合并分支或同步上游前加载 `codeup` Skill；合并方式读取其交付指引，本文只记录项目例外。按该 Skill 的固定调用规则和本机认证指引选择工具与注入入口；本地代码操作使用 Git。

- 读取：使用工作项 API ID 获取内容、评论和关系；展示编号另存为 serialNumber。
- 创建：根据内容选择需求、缺陷或任务类型，补齐负责人和类型要求字段。
- 子项：使用原生 parentId，并验证父子类型合法。
- 相关工作：使用 ASSOCIATED 表示无向关联；可用于跳转和关联项联动，不作为任务领取的阻塞边。
- 阻塞：按 codeup Skill 的关系指引创建原生依赖并双向回读；管理员补齐类型组合后迁移已有文本依赖。实际关系以平台为准，本文只记录配置；不可用时正文写 `Blocked by` 链接并明确其为文本关系。
- ready-for-agent：按上表确认的就绪标记实现，不等同于“开发中”。未完成映射时先提供草案，不声称已打原生标签。
- 代码追踪：分支/提交携带工作项编号；创建 Codeup MR 使用原生 `workItemIds` 并读回确认。
- 实现：按 codeup Skill 的 ProjeX 状态映射判断 frontier；集成证据在平台记录，跨仓库分别核对可使用的基线，不以父需求验收作为所有子任务开始的前提。
- 关闭：以各任务及父需求的验收范围为准；只合入集成分支或 MR 合并本身不自动满足测试、发布或业务验收。
- 联动：按 codeup Skill 的自动化指引读取已配置规则的结果；外部事件只能触发重新核对和获准操作，不能自动扩大执行权限。

列出已创建/更新的真实 URL 和 ID，说明本地检查、CI、合并及验收各自结果。跨仓库项目汇总所有必需 MR；操作中断时保留已完成资源映射，续跑不得重复创建。

## MR 作为分诊入口

对应 Matt 的 `Pull requests as a triage surface`。**MR 作为需求入口：否。**（`triage` 读取此开关；未安装时保持“否”。）

## 发布到工作项追踪

对应 Matt 的 `publish to the issue tracker`。按内容在本项目创建需求、缺陷或任务（见上方“创建”），回读 `id` 与 `serialNumber`。

## 读取相关工作项

对应 Matt 的 `fetch the relevant ticket`。`projex-get-workitem --id <serialNumber 或 API id>`，两者都接受；提交信息后缀 `-#<serialNumber>` 即展示编号。读取评论和关系时用返回的 `id`。

## Wayfinder 操作

对应 Matt 的 `Wayfinding operations`，供 `/wayfinder` 使用，细节按 codeup Skill 的 Wayfinder 映射执行。

- **决策图（Map）**：一个需求，打 `wayfinder:map` 标签，正文为 Destination / Notes / Decisions so far / Not yet specified / Out of scope（Markdown）。
- **子票（Child ticket）**：决策图的任务子项（`--parent-id`），打 `wayfinder:<type>` 标签。
- **阻塞（Blocking）**：原生 `DEPEND_ON`，从被阻塞的票指向 blocker，双向回读。
- **可领取队列（Frontier query）**：决策图 `SUB` 子项中处于未认领状态、且所有 `DEPEND_ON` blocker 已完成的票，按决策图顺序取第一个。
- **认领（Claim）**：状态从未认领推进到开发中对应状态（填写上方状态映射的实际 ID），作为本会话第一个写操作；不以负责人表示认领。
- **解决（Resolve）**：Markdown 评论写答案 → 推进到完成状态 → 在决策图的 Decisions so far 追加一行链接；超出范围的票推进到取消状态，并记入 Out of scope。
