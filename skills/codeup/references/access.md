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

新版是 `aliyun devops codeup-* / projex-* / flow-* / test-hub-*`，例如：

```sh
aliyun devops codeup-list-repositories --page 1 --per-page 20
aliyun devops projex-search-projects --page 1 --per-page 10
aliyun devops flow-list-pipelines --page 1 --per-page 20
```

调用前看具体命令的 `--help`；参数通常为 kebab-case，REST 字段通常为 camelCase，不能机械替换。结构化参数依帮助构造。多行内容先写临时文件；优先使用真实支持的文件参数或结构化工具参数。不要假定每个命令都有 `--body-file`、`--json`、`--all`、`--dry-run`。

区分成功退出码、HTTP 成功和业务成功；创建操作完成后读取返回 ID 对应资源。列表有分页，按响应分页信息取完目标范围；无法确认完整性时标明截断。SearchWorkitems 是只读语义的 POST，不能只凭 HTTP 方法判断风险。

旧 `devops/2021-06-25` API 采用 ROA/AccessKey 签名，与新版 `/oapi/v1` + PAT 不是同一调用协议。只有明确依赖旧接口的项目才走旧版资料，不能把新版 PAT 填入 AK/SK profile。

## 1Password 与执行环境

云效 CLI 使用 PAT；1Password 是凭据来源。先读项目或 Dotfiles 的调用指引，按实际运行 Agent 的机器选择注入方式。

### 桌面集成：减少重复授权

复用仅含 `op://` 引用的 env 模板，通过 `op run --env-file=<已核实模板> -- aliyun devops ...` 注入。macOS 按 TTY 及其创建时间识别会话；同一会话内实际调用会续期，闲置 10 分钟、达到 12 小时上限或 1Password 锁定后须重新授权。弹窗的应用名相同不代表会话相同。

Agent 连续调用时使用任务专用的持久终端。Codex 可用 `exec_command` 启动 Shell 并设置 `tty:true`，保留 `session_id`，后续用 `write_stdin` 发送命令；每次另开一个 PTY 仍是新会话。其他 Agent 使用其持久终端能力；没有时，将已确定的同一阶段命令合并到一次 `op run` 启动的脚本中。2026-10-10 已在 macOS/T3/Codex 验证两次连续注入仅提示一次指纹；其他组合仍需实测。

继续按命令注入短期子进程，任务结束关闭专用终端；不将 PAT 导出至长驻 Shell、不为绕过授权而缓存明文或定时空调用续期。保留输出遮蔽，避免日志打印凭据；锁定后已启动的子进程仍可完成当前操作。

### 无桌面服务器：提供独立凭据通道

远端不会继承 Mac 的 Touch ID 或桌面登录态；复制 `op://` 引用也不提供读取权限，须另有获准读取条目的凭据。按已授权的部署方式选择：

- **下发服务器专用 PAT**：在凭据库保管可单独撤销的 PAT，经已核实的 SSH 通道或部署系统下发，仅存于目标用户的私有配置目录（目录 700、文件 600、仓库外）。运行入口将文件内容作为数据读取，只注入本次 CLI 子进程；不 `source` 凭据文件。关闭 Shell 跟踪；下发失败或内容为空时保留旧凭据，校验后再原子替换。轮换须同步到服务器；不依赖 Mac 持续在线。
- **1Password Service Account**：若账户支持且已授权配置，使用专用保险库、只读 Service Account 和安全注入的 `OP_SERVICE_ACCOUNT_TOKEN`，再运行 `op run`。不能授权访问内置 Personal、Private、Employee 或默认 Shared 保险库。服务账户令牌本身也需要保护，不能放入 Skill、仓库或命令参数。

仅讨论方案不执行凭据下发；不把个人 1Password 登录态部署到共享服务器。共享服务器的 root 可读取文件和进程内存，700/600 不能防 root；若不能接受该边界，使用可信执行环境。服务器专用 PAT 便于单独撤销，但不会自动收窄所属用户的仓库范围，须同时核对令牌权限点与平台成员权限。

配置后在实际 Agent 环境验证身份、目标 Codeup 仓库与 ProjeX 项目的只读查询；只报告退出码和脱敏结果。终端里导出的变量不会自动进入已有的后台服务，可使用按命令注入的运行入口，避免将令牌挂在整个 Agent 服务上。Git SSH/HTTPS 认证另行验证，已有 SSH 密钥不能代替 ProjeX/Flow API 的 PAT。

### 手机直连服务器：全程无需桌面机

手机连接实际运行 Agent 的服务器环境，CLI、Skill、Git 密钥和 API 凭据均在该服务器配置。使用上面的服务器专用 PAT 或 Service Account 后，日常调用无需 Mac 在线或 Touch ID；网络入口、代理和模型认证也须能独立工作。验证时从手机新建服务器上的 Agent 会话，完成目标资源只读查询，不能以 Mac 上的测试代替。

首次配置和轮换也可从手机完成：在云效管理 PAT，用手机凭据管理器保管主副本，通过已核实主机身份的手机 SSH 客户端，以无回显输入将 PAT 写入目标用户的私有文件；输入过程关闭终端录制及 Shell 跟踪，遵循上面的校验与原子替换规则。手机剪贴板如参与传递，使用后清除；普通 Agent 聊天、命令参数和 Shell 历史中不传令牌。应用的私密输入功能仅在已验证能安全投递到目标凭据存储时使用。手机登录 1Password 不会自动授权服务器上的 `op`；已下发 PAT 在过期、撤销或权限变化前可独立使用，轮换仍需更新服务器。

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
- [云效 PAT 权限与有效期](https://help.aliyun.com/zh/yunxiao/user-guide/personal-access-token)
- [1Password 终端授权与会话模型](https://www.1password.dev/cli/app-integration-security)
- [1Password Service Account 与保险库限制](https://www.1password.dev/service-accounts/get-started)
