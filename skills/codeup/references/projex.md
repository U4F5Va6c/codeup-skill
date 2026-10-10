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

## 创建与拆分

读取完整工作项内容、评论及验收标准后再拆分。需求写用户问题、预期结果和验收标准；任务采用可独立验收的纵向切片；缺陷写复现步骤、预期/实际行为与影响范围。

`CreateWorkitem` 的基本必填字段为 `spaceId`、`workitemTypeId`、`subject`、`assignedTo`，项目配置可能要求额外字段。Markdown 描述显式设置 `formatType=MARKDOWN`。先发现类型字段配置和成员 ID；缺少必填负责人时只补问负责人，不猜人选。

按依赖顺序创建：先创建阻塞项，记录真实 API ID，再创建依赖项。设置 `parentId` 前验证允许的父子类型。使用 `projex-list-workitem-relation-workitem-types --id <类型ID> --relation-type <关系类型>`，分别传入 `SUB` 和 `DEPEND_ON` 检查两类约束：允许子任务不代表允许任务间依赖。原生依赖关系只有确认操作和方向后才写；不可用时用正文 `Blocked by` 和工作项链接明确记录，并说明这是文本依赖。不要把普通关联或外部资源关系冒充阻塞。

2026-10-10 实测：默认组织可能未配置 Task → Task 的依赖，查询返回 `[]`，创建返回 400“类型约束”。该约束由组织全局设置的“类型间关系”管理，通常需要管理员；不要擅自改工作项类型或以普通关联替代。依赖允许时，`projex-create-workitem-relation-record --id <依赖方> --workitem-id <被依赖方> --relation-type DEPEND_ON`，随后分别回读依赖方的 `DEPEND_ON` 与被依赖方的 `DEPENDED_BY`。

若用户仅要求拆分和创建子项，保留父项状态，不自动结束父项。发生部分失败时给出已创建项的映射，从失败点继续，避免整批重建。

## Triage 与 ready-for-agent

规范角色为 `needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。它们表达分诊结论/执行准备程度，与“开发中、测试中、已完成”等业务状态分开。

读取 `docs/agents/triage-labels.md` 的实际映射（如果存在）。优先使用已配置原生标签 ID；缺少创建标签能力时，只有项目已约定才能使用自定义字段或正文元数据。报告真实表示方式，不能说“标签已打”却只改正文。

当 `triage` 未安装但 `to-spec` / `to-tickets` 要求 `ready-for-agent` 时，按 issue-tracker 文档的就绪标记规则处理；缺少规则先生成草案并补齐约定，不机械创建五个标签或改业务工作流。

## 状态推进与关闭

更新前回读工作项及工作流，解析目标状态的真实 ID、权限和必填字段；工作流状态列表不自动证明任意两状态可直接跳转。仅更新需要的字段，保留并发修改和原有无关标签。

`UpdateWorkitem` 请求体为字段映射，创建/更新的自定义字段和多值编码可能不同，依当前文档/schema 构造。更新返回无正文也可能成功，必须回读确认。新版 CLI 使用 `--biz-body` 传 JSON；已验证状态字段形状为 `{"status":"<状态ID>"}`，状态值仍须按目标项目查询。

`aliyun-cli-devops 0.9.1` 的 `projex-get-workitem-workflow-info` 要求 `--x-tenant-id`，实测传组织 ID 会返回 401“企业不存在”。先核对官方请求示例；同身份调用官方 `GET /oapi/v1/projex/organizations/{organizationId}/workitems/{id}/workflow` 并省略该头可成功。令牌仍从环境注入，不打印请求头。该响应只列状态，不能替代允许流转方向的验证。

MR 合并后的状态按项目约定进入待测/待验收/完成，不默认等于业务验收。跨仓库工作项应核对所有必需 MR、目标版本 CI 和验收项。已配置的 ProjeX 自动化负责联动时，优先读回结果，避免 Agent 再次推进。

## 来源

- [搜索工作项、筛选与分页](https://help.aliyun.com/zh/yunxiao/developer-reference/searchworkitems)
- [创建工作项](https://help.aliyun.com/zh/yunxiao/developer-reference/createworkitem)
- [字段配置](https://help.aliyun.com/zh/yunxiao/developer-reference/getworkitemtypefieldconfig)
- [工作流状态](https://help.aliyun.com/zh/yunxiao/developer-reference/getworkitemworkflow-get-a-list-of-the-status-of-the-work-item)
- [工作项工作流](https://help.aliyun.com/zh/yunxiao/developer-reference/getworkitemworkflowinfo-get-work-item-workflow-information)
- [更新工作项](https://help.aliyun.com/zh/yunxiao/developer-reference/updateworkitem)
- [研发联动](https://help.aliyun.com/zh/yunxiao/user-guide/devops-linkage)
- [类型间关系配置](https://help.aliyun.com/zh/yunxiao/user-guide/work-item-relationship-customization-settings/)
