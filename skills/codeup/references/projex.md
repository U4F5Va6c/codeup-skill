# ProjeX 工作项

## GitHub 概念如何落地

| GitHub 习惯 | 云效对象 | 必须保留的区别 |
|---|---|---|
| Issue | ProjeX 工作项 | 按需求、缺陷、任务等实际类型创建，具有独立工作流 |
| Projects | ProjeX 项目/项目集、视图、迭代 | 不是代码仓库；一个项目可以跨仓库 |
| Issue number | `serialNumber` + API `id` | 人读编号与接口 ID 分别保存 |
| Labels | 工作项标签或已约定自定义字段 | 标签名称与 ID 不等价，且不等于业务状态 |
| Milestone | 版本或里程碑 | 根据交付日期与业务目的选择；Sprint 对应迭代 |
| Sub-issue | 父子工作项 | 父子关系与阻塞关系分别维护 |
| Blocked by | 项目支持的前后置/依赖关系 | 普通“关联”不一定表达方向和阻塞 |

## 查询与元数据

先发现 `projex-*` 命令或 MCP schema。关键 API 操作包括 `SearchProjects`、`SearchWorkitems`、`GetWorkitem`、`ListWorkitemTypes`、`GetWorkitemTypeFieldConfig`、`GetWorkitemWorkflow`、`GetWorkitemWorkflowInfo`。这些是 API 操作名，不是可直接拼到 `aliyun devops` 后的旧版命令。

`SearchWorkitems` 要求 `spaceId` 和 `category`，单次不能跨多个项目搜索。多个项目逐一查询、保留项目归属并去重。`category`（如 Req、Bug、Task）与 `workitemTypeId` 是两层概念；类型 ID 必须从项目配置查得。

查询筛选 `conditions` 是 JSON 字符串，里面的字段、运算符和选项依真实元数据或官方示例。不要把显示名称填进 ID，也不要把嵌套对象当成已编码字符串。分页响应提供 `x-next-page` 等信息，CLI 是否暴露这些信息需现场核对。

2026-10-11 中心版实测：`projex-get-workitem --id` 同时接受 API `id` 和展示编号 `serialNumber`（如提交后缀 `-#PROJ-12` 中的 `PROJ-12`），返回中的 `id` 用于后续写操作。网页链接用展示编号：`https://devops.aliyun.com/projex/req/<serialNumber>`、`.../projex/task/<serialNumber>`，打开后跳转到项目内详情页。

## 创建与拆分

读取完整工作项内容、评论及验收标准后再拆分。内容与结构沿用当前流程 Skill、用户要求及项目约定；发布格式按 [Markdown 与富文本](text-format.md) 适配。

`CreateWorkitem` 的基本必填字段为 `spaceId`、`workitemTypeId`、`subject`、`assignedTo`，项目配置可能要求额外字段。先发现类型字段配置和成员 ID；缺少必填负责人时只补问负责人，不猜人选。

按依赖顺序创建：先创建阻塞项，记录真实 API ID，再创建依赖项。设置 `parentId` 或添加依赖前，按下节分别验证类型约束与方向。

若用户仅要求拆分和创建子项，保留父项状态，不自动结束父项。发生部分失败时给出已创建项的映射，从失败点继续，避免整批重建。

## 父子、关联与依赖

关系要按具体类型判断：详情页的“关联项”可对应无向的 `ASSOCIATED`，用于相关工作跳转，也可配置关联项联动；它不说明谁阻塞谁。父子使用 `PARENT` / `SUB`，依赖方使用 `DEPEND_ON`，反向为 `DEPENDED_BY`。读取 `projex-list-workitem-relation-records --id <工作项ID> --relation-type <关系类型>` 确认记录，不凭页面有“关联”按钮推断全部关系能力。

需求拆成实现任务时，先用父子关系表达范围归属；只有某项工作确实要等待另一项的输出，才增加有向依赖。父需求等待子任务完成后整体验收属于汇总规则，无需为每对子项再建依赖；任务等待另一个需求交付的服务或制品时，才考虑对应的跨类型依赖。

先用 `projex-list-workitem-relation-workitem-types --id <当前工作项的类型ID> --relation-type <关系类型>` 查询允许的目标类型；核对子项时传 `SUB`，核对阻塞项时传 `DEPEND_ON`。`--id` 在这个查询中是**类型 ID**，下面的关系读写则使用**工作项 ID**。检查返回的 `workitemTypeList` 是否包含目标类型；任务间、需求间可用不代表任务与需求之间可用。

若 B 必须等 A，则 B 是依赖方、A 是支撑方。通过本机凭据入口执行以下子命令：

```sh
projex-list-workitem-relation-records --id <B的工作项ID> --relation-type DEPEND_ON
projex-create-workitem-relation-record --id <B的工作项ID> --workitem-id <A的工作项ID> --relation-type DEPEND_ON
projex-list-workitem-relation-records --id <B的工作项ID> --relation-type DEPEND_ON
projex-list-workitem-relation-records --id <A的工作项ID> --relation-type DEPENDED_BY
```

已有同一依赖就跳过创建。核对 B 的记录 `resourceId` 为 A、A 的反向记录 `resourceId` 为 B；两端的关系记录 `id` 可以不同。一次创建会生成反向记录，无需再创建 A → B 的依赖。页面应在 B 的“依赖项”看到 A、A 的“支撑项”看到 B。父子与普通关联可同时存在，保留其原有用途；任务图避免自依赖和循环依赖。

需要移除获准的依赖时，用 `projex-delete-workitem-relation-record --id <B的工作项ID> --workitem-id <A的工作项ID> --relation-type DEPEND_ON`，再回读两端确认该边消失；参数不使用关系记录 ID。测试只清理本次创建的临时边，并核对原有状态、父子与其他关系。

类型约束由组织全局设置的“类型间关系”管理，通常需要管理员。缺少目标组合时只补实际需要的有向类型组合；“全部类型 → 全部类型”可能与已有规则重叠。管理员调整后重新查询，旧的空列表或 400“类型约束”不再作为当前结论。原生依赖确实不可用时，在平台正文用 `Blocked by` 链接明确记录文本依赖；启用后补齐真实边，不新建本地依赖台账。

## Triage 与 ready-for-agent

规范角色为 `needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。它们表达分诊结论/执行准备程度，与“开发中、测试中、已完成”等业务状态分开。

读取 `docs/agents/triage-labels.md` 的实际映射（如果存在）。优先使用已配置原生标签 ID；缺少创建标签能力时，只有项目已约定才能使用自定义字段或正文元数据。报告真实表示方式，不能说“标签已打”却只改正文。

当 `triage` 未安装但 `to-spec` / `to-tickets` 要求 `ready-for-agent` 时，按 issue-tracker 文档的就绪标记规则处理；缺少规则先生成草案并补齐约定，不机械创建五个标签或改业务工作流。

## Wayfinder 映射

`wayfinder` 的 map 是一个需求，decision ticket 是它的任务子项；先按上节核对需求 → 任务的 `SUB` 与任务间 `DEPEND_ON`。标签 `wayfinder:map` 与 `wayfinder:research|prototype|grilling|task` 是项目原生标签：`projex-list-labels --id <projectId>` 查重，缺失时 `projex-create-label` 创建，ID 记入 tracker，创建时用 `--labels` 附加。决策票不打 `ready-for-agent`。

**认领用状态，不用负责人。** wayfinder 以“无 assignee”表示未认领，而 ProjeX 创建时必填 `assignedTo`，所有票天生有负责人。按 tracker 映射：初始状态（如待处理）= 未认领，认领 = 推进到开发中对应状态（如处理中），作为本会话第一个写操作并回读；解决 = 完成状态；判定超出范围 = 取消状态。

**Frontier**：`projex-list-workitem-relation-records --id <map> --relation-type SUB` 取子项；保留处于未认领状态的；再对每项读 `DEPEND_ON`，所有 blocker 都已到终态（完成或取消）才算解除阻塞。map 正文不列未关闭的票，按子项创建顺序取最早的一个：`SUB` 记录默认新的在前，CLI 的 `sort_by` 对 `gmtCreate` 报错，取出后在本地排序。用 `--cli-query 'status.id'`、`'[].resourceId'` 只取所需字段。

**Resolve**：答案用 [Markdown 评论脚本](text-format.md#projex-评论固定使用-markdown-脚本) 写入并按 ID 回读，再推进到完成状态。map 的 Decisions so far 通过读回 `description`、追加一行 `- [<票标题>](https://devops.aliyun.com/projex/task/<serialNumber>)：<一句结论>`、以 `{"description":...,"formatType":"MARKDOWN"}` 整体更新；读和写之间不插入其他编辑，避免覆盖并发修改。research 票的分支只推送，不建 MR。

## 状态推进与关闭

### Matt 执行阶段与业务状态

执行阶段不是平台固定状态名。先在项目 tracker 中将下面的语义映射到各工作项类型的实际状态 ID、允许流转和验收范围；可复用现有字段/标签，没有对应状态时用工作项证据表达，不强制扩展工作流。

| 事实或阶段 | 推进依据与负责方 |
|---|---|
| 规格/切片可领取 | 按 to-spec / to-tickets 完成相应审阅与就绪标记；协调 Agent 还须检查所有 blocker 的证据和任务是否已被领取 |
| 正在实现 | 实现者已领取明确范围，记录目标仓库和分支；ready-for-agent 标签本身不表示已开工 |
| 实现已集成、可供后继使用 | merger/协调 Agent 确认所需代码已进入约定集成分支，相关检查通过；在工作项保存仓库、分支、SHA 和证据，后继任务从包含该结果的基线开始 |
| 可评审或交付 | 按 implement-spec 执行整体 code-review，保留 Standards/Spec 审阅结论；MR 就绪、平台审批和必需 CI 各自验证 |
| 任务可关闭 | 满足这张任务自身的验收范围；默认核对其必需 MR 已合入目标分支及相关验证，项目明确只交付集成分支时才以该边界完成 |
| 父需求可关闭 | 汇总所有必需任务、仓库 MR 和集成验收；要求部署/业务验收时还须取得对应结果，不由子项完成或一次 MR 事件推断 |

`implement-spec` 的 frontier 用项目约定的“阻塞已解除”判断，不机械等同于 ProjeX 的“已关闭”。例如 A 的代码已集成并验证，B 可以使用该结果开始；A 仍可等待最终 MR 或业务验收。默认仅当后继依赖的是该集成结果时才如此解除；需要已部署服务或发布制品的依赖，应等待对应证据。已有任务验收要求优先，不能为了调度方便提前关闭。

关系图描述谁依赖谁，运行证据决定条件是否满足；ProjeX 原生依赖不会自动运行 Agent。实现被撤回、基线不再包含依赖结果或验证失效时，重新评估受影响 frontier。动态证据保存在平台工作项/MR，tracker 只保存判定规则。

Matt 的 draft PR closing 语义映射为 Codeup 原生工作项关联与项目关闭规则，不机械照搬 `Closes`。若当前 Codeup 能力没有等价 draft 标志，按项目方式标明未就绪并保留合并限制；没有 MR 的集成分支交付也不自动代表业务需求完成。

### 执行状态更新

更新前回读工作项及工作流，解析目标状态的真实 ID、权限和必填字段；工作流状态列表不自动证明任意两状态可直接跳转。仅更新需要的字段，保留并发修改和原有无关标签。

`UpdateWorkitem` 请求体为字段映射，创建/更新的自定义字段和多值编码可能不同，依当前文档/schema 构造。更新返回无正文也可能成功，必须回读确认。新版 CLI 使用 `--biz-body` 传 JSON；已验证状态字段形状为 `{"status":"<状态ID>"}`，状态值仍须按目标项目查询。

`aliyun-cli-devops 0.9.1` 的 `projex-get-workitem-workflow-info` 要求 `--x-tenant-id`，实测传组织 ID 会返回 401“企业不存在”。先核对官方请求示例；同身份调用官方 `GET /oapi/v1/projex/organizations/{organizationId}/workitems/{id}/workflow` 并省略该头可成功。令牌仍从环境注入，不打印请求头。该响应只列状态，不能替代允许流转方向的验证。

状态写入由项目约定的 Agent、自动化或人工负责，同一转换明确一个主要负责方。已配置自动化时先读回状态与执行记录；异常时按 [自动化指引](automation.md) 核查，不让 Agent 与规则反复覆盖。

## 来源

- [搜索工作项、筛选与分页](https://help.aliyun.com/zh/yunxiao/developer-reference/searchworkitems)
- [创建工作项](https://help.aliyun.com/zh/yunxiao/developer-reference/createworkitem)
- [字段配置](https://help.aliyun.com/zh/yunxiao/developer-reference/getworkitemtypefieldconfig)
- [工作流状态](https://help.aliyun.com/zh/yunxiao/developer-reference/getworkitemworkflow-get-a-list-of-the-status-of-the-work-item)
- [工作项工作流](https://help.aliyun.com/zh/yunxiao/developer-reference/getworkitemworkflowinfo-get-work-item-workflow-information)
- [更新工作项](https://help.aliyun.com/zh/yunxiao/developer-reference/updateworkitem)
- [研发联动](https://help.aliyun.com/zh/yunxiao/user-guide/devops-linkage)
- [类型间关系配置](https://help.aliyun.com/zh/yunxiao/user-guide/work-item-relationship-customization-settings/)
- [可关联的工作项类型](https://help.aliyun.com/zh/yunxiao/developer-reference/listworkitemrelationworkitemtypes)
- [创建工作项关系](https://help.aliyun.com/zh/yunxiao/developer-reference/createworkitemrelationrecord)
- [读取工作项关系](https://help.aliyun.com/zh/yunxiao/developer-reference/listworkitemrelationrecords)
- [删除工作项关系](https://help.aliyun.com/zh/yunxiao/developer-reference/deleteworkitemrelationrecord)
