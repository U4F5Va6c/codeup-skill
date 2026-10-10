# 代码交付

## 从工作项到 Git

1. 读工作项与验收标准，查项目指定代码库，核对本地 remote、分支和未提交改动。
2. 从项目约定基线建短期分支；分支含工作项编号便于追踪，具体格式服从现有规范。
3. 实现并运行仓库要求的相关检查。提交前审阅 diff，只提交本次范围的文件。
4. 使用 Git 提交/推送，保留用户现有提交格式。只有在项目有证据时才使用关联语法。

当前用户约定示例：`fix-登录模块-修复会话过期跳转-#AUTH-123`。其中 `AUTH-123` 只是格式示意，需替换为真实编号。官方支持 Commit Message 中 `#ID` 关联工作项；编号语法、仓库关联权限需在项目首次接入时实测，并回读关联记录。不要将 `Closes #123` 当成云效自动关闭契约。

## 创建与评审合并请求

Codeup UI 通常称合并请求，API 名称为 `ChangeRequest`；可以称 PR/MR，但调用云效 API。先查询相同源库、源分支、目标库、目标分支的已有请求，避免重复。

通过 `codeup-*` 命令帮助或 MCP schema 查明创建参数。官方 `CreateChangeRequest` 使用：

- `sourceBranch`、`targetBranch`：真实分支。
- `sourceProjectId`、`targetProjectId`：数字代码库 ID，**不是 ProjeX projectId**。
- `title`、`description`；正文使用 [合并请求模板](../assets/merge-request.md)。
- `workItemIds`：关联的工作项 API ID，REST 形状是逗号分隔字符串。
- `reviewerUserIds`：实际用户 ID 列表（需要指定评审人时）。

用接口参数建立原生工作项关联，并回读验证；正文链接作为可读证据。仅有链接而无原生关联时明确说明，不能宣称原生追踪已建立。`projex-list-workitem-ext-relation-records --id <工作项ID> --category codeupMergeRequest` 可回读原生 MR 关联；核对 `businessId`、`projectId` 和 `url`，不要只看创建请求参数。创建后记录仓库 ID、`localId`、`bizId`、源 SHA 及服务端 URL。

评审前读取详情、diff、已有评论和最新 patch set。行内评论需匹配正确文件、左右侧行号和 patch set；不同评论/比较接口的 from/to 语义可能不同，以各接口定义为准。更新后重新定位过期评论，不复用旧行号。原生评论解决状态与代码修改状态分别验证。

## 测试、Flow 与发布

| 目的 | 执行位置 | 完成证据 |
|---|---|---|
| 单元/集成/端到端测试 | 仓库现有测试工具或 CI runner | 命令、退出码、必要报告及对应 SHA |
| 持续集成 | Flow 流水线及其 jobs | pipelineId、runId、源 SHA、必需 job 结论 |
| 测试计划与人工验收记录 | Testhub | 测试用例/计划/结果 ID，实际执行证据 |
| 部署发布 | 已配置 Flow 发布阶段或 AppStack | 环境、制品/版本、发布单/运行状态 |

创建 Testhub 用例前查询字段配置与 `test-hub-list-directories`。0.9.1 帮助将 `--directory-id` 标为可选，但实测缺少它会返回“目录id不能为空”；使用目标库回读的目录 ID。测试计划、用例、计划中的执行结果是不同对象。`test-hub-update-test-result` 的 `--id` 是用例 ID，`--testplan-id` 是计划 ID；先用计划用例评论保存命令、SHA 和实际执行结果，再更新结果并回读计划统计。

Testhub 管理记录不能替代运行测试；调用创建流水线运行接口也不表示 CI 已通过。读取各 job 和终态，处理等待人工确认、失败、取消、超时和未知状态。最新成功运行如果不对应 MR 当前 SHA，不可作为合并依据。

首次接入先用 `flow-list-service-connections --service-connection-type Codeup` 查询连接。YAML 的 `certificate.serviceConnection` 使用服务连接 UUID（列表的 `uuid`）；回读流水线会解析成数字 `serviceConnectionId`。连接缺失时需按已授权范围配置；个人私密连接可在 Flow 页面创建，PAT 权限不等于浏览器账号的服务授权。不要将 PAT 写入 YAML 代替服务连接。

首次触发前读取流水线定义，区分只构建、自动部署和手工发布阶段。用户授权运行测试不自动授权生产部署。流水线变更复用当前配置，确认真实 service connection、runner、制品仓库和环境，不套入别的组织 ID。

CI 失败先读取与本次 SHA 对应的失败 job 日志并脱敏，再修复。`flow-get-pipeline-job-run-log --job-id` 使用运行详情中 stage 的 job ID，不是 actions 日志链接里的执行 ID。首次接入打印语言版本；镜像名称不能证明运行时版本与本机一致。写入测试结果必须来源于实际执行；无法执行就标未验证。创建运行超时先查询是否已启动，避免重复构建/部署。

## 合并与验收

在授权合并时，重新检查源 SHA、Codeup 合并门禁、冲突结果、评审状态和目标 SHA 的必需检查。未知状态不是通过；源 SHA 变化后重新验证。保持受保护分支规则，使用允许的合并策略，不使用忽略门禁参数。

API 若无原子 expected-head 条件，本地预检不能消除并发推送竞态；依靠服务端门禁并在合并后回读实际结果，不宣称预检是原子保证。合并后分别核对 MR 状态、合并提交、CI/部署和工作项验收。

在 T3 Code 中，若当前版本支持该 URL/provider，使用其 `link_pull_request` 关联线程，并在结束前检查关联结果。工具拒绝 Codeup URL 时报告限制、保留普通链接；安装本 Skill 不会为 T3 原生 UI 添加 provider。2026-10-10 实测 `link_pull_request` 拒绝 Codeup 的 `/change/<localId>` URL；这不影响 Codeup/ProjeX 原生关联，不能改成 GitHub 路径来伪造线程关联。

## 来源

- [创建合并请求与 workItemIds](https://help.aliyun.com/zh/yunxiao/developer-reference/createchangerequest-create-merge-request)
- [合并合并请求](https://help.aliyun.com/zh/yunxiao/developer-reference/mergechangerequest-merge-merge-request)
- [提交关联工作项](https://help.aliyun.com/zh/yunxiao/user-guide/how-to-associate-requirements-tasks-defects-when-code-is-submitted)
- [工作项关联研发资产](https://help.aliyun.com/zh/yunxiao/user-guide/associated-r-d-assets)
- [Flow 代码源与服务连接](https://help.aliyun.com/zh/yunxiao/user-guide/pipeline-sources)
- [Flow 创建流水线](https://help.aliyun.com/zh/yunxiao/developer-reference/createpipeline-create-pipeline)
- [Flow 任务运行日志](https://help.aliyun.com/zh/yunxiao/developer-reference/getpipelinejobrunlog)
- [Testhub 创建用例](https://help.aliyun.com/zh/yunxiao/developer-reference/createtestcase)
- [Testhub 更新测试结果](https://help.aliyun.com/zh/yunxiao/developer-reference/updatetestresult)
