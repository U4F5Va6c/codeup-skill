# 代码交付

## 从工作项到 Git

1. 读工作项与验收标准，查项目指定代码库，核对本地 remote、分支和未提交改动。
2. 从项目约定基线建短期分支；分支含工作项编号便于追踪，具体格式服从现有规范。
3. 实现并运行仓库要求的相关检查。提交前审阅 diff，只提交本次范围的文件。
4. 使用 Git 提交/推送，保留用户现有提交格式。只有在项目有证据时才使用关联语法。

当前用户约定示例：`fix-登录模块-修复会话过期跳转-#AUTH-123`。其中 `AUTH-123` 只是格式示意，需替换为真实编号。官方支持 Commit Message 中 `#ID` 关联工作项；编号语法、仓库关联权限需在项目首次接入时实测，并回读关联记录。不要将 `Closes #123` 当成云效自动关闭契约。

## 分支角色与默认合并策略

子任务分支承载一张任务票；集成分支汇总同一需求的多张任务票，完成整体测试和评审后再交付目标主分支。这是 Matt `implement-spec` 的协作角色，不是 Git 的特殊分支类型。单个小改动可直接使用一个功能分支和一个 MR，无需创建集成分支。

下表是本 Skill 的默认约定。用户明确指示或项目已写明的策略优先；执行前还须核对平台允许的方式与分支保护。默认方式不可用且没有明确替代约定时，说明冲突并请用户选择，不静默改用另一种方式。

| 合并方向 | 默认策略 | 目的 |
|---|---|---|
| 子任务分支 → 集成分支 | 能快进时 Fast-forward；历史分叉时 Merge Commit | 保留各任务的原始提交与祖先关系，便于继续集成 |
| 短期功能/修复分支或集成分支 → 目标主分支 | Squash | 一个 MR 形成一个交付提交；主分支名称从仓库读取 |
| 上游 → Fork 的上游镜像分支 | 仅 Fast-forward | 保持与上游相同的提交历史；分叉时先查明原因 |
| 上游 → Fork 的长期定制分支 | 能快进时 Fast-forward；历史分叉时 Merge Commit | 保留上游祖先关系，支持持续同步，不做 Squash |

先按分支用途选择策略，不能仅凭目标叫 `main` 就 Squash。长期维护分支间的其他合并按项目约定处理。同步上游时，在用于提 MR 的同步分支上操作也遵循保留上游历史的规则。

本地 Git 快进使用 `git merge --ff-only <源分支>`；确认历史已分叉且允许创建合并提交时使用 `git merge --no-ff <源分支>`。快进失败可能是错误或状态异常，不把任意失败当作自动执行另一种合并的信号。

云效 CLI `codeup-merge-change-request` 要求显式传入 `--merge-type`：`ff-only`、`no-fast-forward`、`squash` 分别对应上述三种方式；`rebase` 仅在明确约定时选择。按已选凭据入口调用，以当前 `--help` 核对参数，不依赖网页预选项或 CLI 隐含默认值。参数于 2026-10-11 对照 `aliyun-cli-devops 0.9.1` 帮助核对。

Squash 提交遵循项目提交格式。MR 保留规格与所有相关任务的原生关联和说明，不能依赖被压缩掉的中间提交完成追踪；工作项仍按验收规则关闭。Squash 后的新任务从更新后的目标分支开始，避免继续复用已合并的短期分支。

## 创建与评审合并请求

Codeup UI 通常称合并请求，API 名称为 `ChangeRequest`；可以称 PR/MR，但调用云效 API。先查询相同源库、源分支、目标库、目标分支的已有请求，避免重复。

通过 `codeup-*` 命令帮助或 MCP schema 查明创建参数。官方 `CreateChangeRequest` 使用：

- `sourceBranch`、`targetBranch`：真实分支。
- `sourceProjectId`、`targetProjectId`：数字代码库 ID，**不是 ProjeX projectId**。
- `title`、`description`：内容与结构遵循当前流程 Skill、用户与项目约定；[合并请求模板](../assets/merge-request.md) 仅供缺少约定时参考，发布格式见 [Markdown 与富文本](text-format.md)。
- `workItemIds`：关联的工作项 API ID，REST 形状是逗号分隔字符串。
- `reviewerUserIds`：实际用户 ID 列表（需要指定评审人时）。

用接口参数建立原生工作项关联，并回读验证；正文链接作为可读证据。仅有链接而无原生关联时明确说明，不能宣称原生追踪已建立。`projex-list-workitem-ext-relation-records --id <工作项ID> --category codeupMergeRequest` 可回读原生 MR 关联；核对 `businessId`、`projectId` 和 `url`，不要只看创建请求参数。创建后记录仓库 ID、`localId`、`bizId`、源 SHA 及服务端 URL。

评审前读取详情、diff、已有评论和最新 patch set。行内评论需匹配正确文件、左右侧行号和 patch set；不同评论/比较接口的 from/to 语义可能不同，以各接口定义为准。更新后重新定位过期评论，不复用旧行号。原生评论解决状态与代码修改状态分别验证。

Matt `code-review` 的独立 Standards/Spec 审阅、平台账号审批、CI 是不同证据；自身 diff 检查不能代替独立审阅，同一 PAT 不能冒充第二位审批人。任务何时可供后继使用及何时关闭，按 [状态映射](projex.md#matt-执行阶段与业务状态) 判断。

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

自动 MR CI 在 Codeup 代码源配置 `triggerEvents: [mergeRequestOpenedOrUpdate]`；2026-10-11 隔离项目实测，MR 新建与源分支后续推送均自动运行。`branch` 指定默认运行分支，不能仅凭它宣称已限制 MR 目标分支；所需事件过滤另行核对。仓库内保存 YAML 不会自行更新 Flow：同步服务端并回读事件配置。Flow 的事件订阅与 ProjeX 状态联动的 Hook 分别维护。

在 Codeup 目标分支保护中限制直接推送，并把该 Flow 流水线设为必需检查。首次接入用获准的临时失败测试验证“自动触发 → CI 失败 → 普通合并被拒”，移除探针后验证当前 SHA 的必需检查成功；再次推送应重新等待新版本检查。使用 `codeup-list-change-request-patch-sets` 找到最新源版本，再用 `codeup-list-change-request-ci-check-list --patch-set-biz-id` 核对必需项、运行与结果。临时失败测试在最终交付差异中移除，证据留在 MR/Flow。

CI 失败先读取与本次 SHA 对应的失败 job 日志并脱敏，再修复。`flow-get-pipeline-job-run-log --job-id` 使用运行详情中 stage 的 job ID（`flow-get-pipeline-run --cli-query 'stages[].stageInfo.jobs[].id'`），不是 actions 日志链接里的执行 ID。日志的 `content` 是一整段字符串，含带 STS `security-token` 的步骤下载签名 URL：用 `--cli-query content` 取出后按行过滤需要的行，不整段打印、粘贴或写入评论。首次接入打印语言版本；镜像名称不能证明运行时版本与本机一致。写入测试结果必须来源于实际执行；无法执行就标未验证。创建运行超时先查询是否已启动，避免重复构建/部署。

## 合并与验收

在授权合并时，按[默认合并策略](#分支角色与默认合并策略)确定方式，重新检查源 SHA、Codeup 合并门禁、冲突结果、评审状态和目标 SHA 的必需检查。对照项目要求核对实际配置的检查项；空要求列表上的 `allRequirementsPass: true` 不能证明所需门禁已启用。未知状态不是通过；源 SHA 变化后重新验证。保持受保护分支规则，不使用忽略门禁参数。

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
