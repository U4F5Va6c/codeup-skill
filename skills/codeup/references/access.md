# 访问与工具选择

## 官方新版 CLI

检查 `command -v aliyun`、`aliyun version` 及已安装插件。需要安装且在任务授权范围内时，按官方安装说明安装 CLI，再显式安装云效插件：

```sh
aliyun plugin install --names aliyun-cli-devops
aliyun devops version
aliyun devops --help
```

显式安装可避免业务命令等待交互式插件安装。不要为了一个任务修改全局自动安装策略。`version` 成功只证明程序可用，需对目标资源做最小只读查询才能验证认证及权限。

中心版默认 API 为 `https://openapi-rdc.aliyuncs.com`，使用以下环境变量：

- `ALIBABA_CLOUD_YUNXIAO_ACCESS_TOKEN`：PAT，通过执行环境的安全凭据通道注入。
- `ALIBABA_CLOUD_YUNXIAO_ORGANIZATION_ID`：组织 ID，必须与本次项目一致。

Region 版使用 PAT 和 `ALIBABA_CLOUD_YUNXIAO_API_BASE_URL`，接入地址取自该实例；不照搬中心版组织路径。站点类型以项目配置和实例资料确定，不能仅凭某个环境变量存在就推断。

API Token 不放进 Skill、仓库、命令参数、URL、报告或聊天。T3 Code 场景下凭据需提供给实际运行 Agent 的 environment/server；手机或交互式终端的变量不会自动出现在服务器进程中。禁止从仓库自动 `source .env` 获取令牌，因为这会执行仓库提供的 Shell 代码。

若项目使用 1Password，先读项目或 Dotfiles 的云效调用指引，复用仅含 `op://` 引用的 env 模板，通过 `op run --env-file=<已核实模板> -- aliyun devops ...` 注入。模板不含明文令牌；跨设备需各自配置可用的凭据通道，不能把本机登录态当作服务器授权。

新版是 `aliyun devops codeup-* / projex-* / flow-* / test-hub-*`，例如：

```sh
aliyun devops codeup-list-repositories --page 1 --per-page 20
aliyun devops projex-search-projects --page 1 --per-page 10
aliyun devops flow-list-pipelines --page 1 --per-page 20
```

调用前看具体命令的 `--help`；参数通常为 kebab-case，REST 字段通常为 camelCase，不能机械替换。结构化参数依帮助构造。多行内容先写临时文件；优先使用真实支持的文件参数或结构化工具参数。不要假定每个命令都有 `--body-file`、`--json`、`--all`、`--dry-run`。

区分成功退出码、HTTP 成功和业务成功；创建操作完成后读取返回 ID 对应资源。列表有分页，按响应分页信息取完目标范围；无法确认完整性时标明截断。SearchWorkitems 是只读语义的 POST，不能只凭 HTTP 方法判断风险。

旧 `devops/2021-06-25` API 采用 ROA/AccessKey 签名，与新版 `/oapi/v1` + PAT 不是同一调用协议。只有明确依赖旧接口的项目才走旧版资料，不能把新版 PAT 填入 AK/SK profile。

## 官方 MCP

中心版官方托管地址：`https://openapi-rdc.aliyuncs.com/ai/mcp`；Region 版用实例自己的 `/ai/mcp`。优先复用已有连接，按客户端实际能力选择 OAuth 或安全注入的 Bearer Token。

只选择需要的工具集，例如 `code-management,project-management`；CI 或测试任务再加入 `pipeline-management,test-management`。筛选工具集只减少上下文，不是服务端权限控制；仍需最小范围 PAT 和项目授权。

本地 stdio 的官方包是 `alibabacloud-devops-mcp-server`，其环境变量是 `YUNXIAO_ACCESS_TOKEN`、Region 专用 `YUNXIAO_API_BASE_URL`，与 CLI 不同。按官方运行时要求与团队锁定版本安装。不同客户端的 MCP 配置语法不同，不把 Claude JSON 原样写入 Codex 配置。

发现当前连接暴露的工具和 schema 后调用；CLI 与 MCP 覆盖范围不保证相等。MCP 缺少合并、标签或关系操作时，使用已认证且目标相同的官方 CLI；不要冒充操作已完成。

## 第三方 codeup-cli（可选）

`JilunSun7274/codeup-cli` 的 v0.6.0（`f80472e`）提供 repo/branch/pr/auth 命令和结构化输出，适合已有使用者。它不是 `gh` 的可替换实现，也不提供 ProjeX、Flow、Testhub 工作流。

该版本 `pr create` 未暴露 `workItemIds`，建仓组默认限制为 `modelbest`（可配置），API 路径按中心版构造。若使用它，先核对版本及限制；工作项关联应走官方工具。不要借 `--ignore-gate` 绕过未通过的门禁。

## 写操作重试

读请求的临时错误可有限重试并遵循服务端限流提示。创建 MR、工作项、评论、流水线运行时，超时不等于失败；用返回 ID 或精确范围回读，排除已创建结果后才重试。仍有歧义则报告待确认，避免重复写入。

## 来源

- [官方 CLI 安装与新版插件](https://help.aliyun.com/zh/yunxiao/developer-reference/how-to-install-initialize-and-use-the-apsara-devops-cli)
- [官方 MCP、认证与工具集](https://help.aliyun.com/zh/yunxiao/developer-reference/cloud-effect-mcp-tool-instructions)
- [API 入口：新版与旧版](https://help.aliyun.com/zh/yunxiao/developer-reference/)
- [服务接入点](https://help.aliyun.com/zh/yunxiao/developer-reference/service-access-point-domain)
