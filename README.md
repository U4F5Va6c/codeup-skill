# Codeup Skill

让 Claude Code、Codex 等支持 Agent Skills 的工具，使用阿里云云效管理需求、代码评审、测试和交付。采用 GitHub 常见协作习惯，保留 Codeup、ProjeX、Flow、Testhub 各自的资源、ID 和工作流语义。

这是工作流 Skill，不是 CLI、MCP 服务或 T3 Code 插件。它不包含凭据，也不会仅靠安装就在 T3 的界面中新增 Source Control。

## 安装

```sh
npx -y skills add U4F5Va6c/codeup-skill -g -a claude-code codex -s codeup -y
```

完整内容安装到 `~/.agents/skills/codeup`，Claude Code 使用安装器建立的引用。新会话中用 `$codeup`（Codex）或 `/codeup`（Claude Code）调用。

需要固定版本时安装已发布标签：

```sh
npx -y skills add https://github.com/U4F5Va6c/codeup-skill/tree/v0.3.0/skills/codeup -g -a claude-code codex -s codeup -y
```

跟随主分支安装的用户可运行 `npx skills update -g -y`（会检查其他已安装 Skills）。固定版本或通过 Dotfiles 快照安装的用户应显式选择新版本再安装。

## 接入项目

1. 默认配置官方新版 `aliyun devops` 插件；已有官方云效 MCP 可沿用。记录各执行机器的凭据入口，Skill 按[环境选择规则](skills/codeup/references/access.md#按执行环境选择凭据入口)发现并复用；桌面 1Password、服务器包装命令、CI 密钥注入分别处理。随包 API 脚本需 Python 3，并复用同一注入通道。Git 推送认证单独配置。
2. 使用 [项目绑定模板](skills/codeup/assets/issue-tracker.md)，核对组织、ProjeX 项目、Codeup 仓库、工作项类型、必填字段与验收规则。不要提交 Token。
3. 在项目的 Agent 指令中引用绑定文档和本 Skill。调用 `setup-matt-pocock-skills` 时按其 Other tracker 扩展方式接入，详见 [接入说明](skills/codeup/references/repository-setup.md)。Matt Skills 需要另行安装。
4. 在测试项目跑通读取工作项、测试、推送、MR 原生关联、当前 SHA 的 CI 检查，再逐步启用写操作。

使用示例：

> 使用 codeup 读取当前 ProjeX 需求，核对验收标准，完成修改和测试后创建关联该工作项的 Codeup 合并请求。

## 内容与范围

| 入口 | 用途 |
|---|---|
| [SKILL.md](skills/codeup/SKILL.md) | 任务路由、资源身份、授权与结果核验 |
| [访问](skills/codeup/references/access.md) | 官方 CLI/MCP、认证、API 版本与分页 |
| [文本格式](skills/codeup/references/text-format.md) | Markdown 发布、ProjeX 评论脚本与平台渲染限制；内容结构由当前流程决定 |
| [ProjeX](skills/codeup/references/projex.md) | 需求、缺陷、任务、字段、依赖与状态 |
| [交付](skills/codeup/references/delivery.md) | Git、MR、评审、Flow、Testhub 与验收 |
| [工具选择](docs/tooling.md) | 与 gh、第三方 codeup-cli、T3 Provider 的边界 |

2026-10-10 已在隔离云效资源验证工作项父子关系、独立工作树实现、CLI 测试、推送、MR 原生关联与 Agent 评审、准确提交的 Flow CI，以及 Testhub 执行记录。原生任务依赖受组织关系类型配置限制，完整流程验收仍未通过；T3 的 Codeup MR 线程关联尚不支持。包结构、相对链接和可移植性检查已通过；API 参数以当前官方文档和已安装工具 schema 为准。

## 维护

本仓库是唯一开发源。个人 Dotfiles 的 `agents/skills/own/codeup` 可保存按提交固定的部署快照；快照不单独编辑。其他设备从自己的 Dotfiles 克隆安装，或直接从本仓库安装，二选一。

验证、发布及场景回归见 [CONTRIBUTING.md](CONTRIBUTING.md)。问题通过本仓库 Issues 跟踪，修订通过 PR 审阅；提交前删除所有公司资源、日志、账号和凭据。

MIT License。与阿里云、Matt Pocock、Anthropic、OpenAI 和 T3 Code 无官方隶属关系。
