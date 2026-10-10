# 工具与职责

核查日期：2026-10-10。

| 层次 | 职责 |
|---|---|
| Git | 本地代码、分支、提交与推送 |
| 官方新版云效 CLI / MCP | Codeup、ProjeX、Flow、Testhub 的资源访问 |
| codeup Skill | 术语映射、项目规则、Matt Skills 适配与验收证据 |
| 项目 tracker 文档 | 组织、仓库、字段、状态和就绪标记的实际绑定 |
| T3 原生 Provider | 客户端内的仓库、MR、评审和检查能力；需要独立开发 |

GitHub Issue 对应 ProjeX 工作项，但需区分需求、缺陷和任务的类型、字段及工作流。GitHub PR 对应 Codeup 合并请求；GitHub Actions 的常见职责分散在 Flow、代码门禁和部署服务中。Testhub 保存测试管理记录，不执行仓库的单元测试。

## 推荐后端

使用 [官方新版云效 CLI](https://help.aliyun.com/zh/yunxiao/developer-reference/how-to-install-initialize-and-use-the-apsara-devops-cli) 的 `aliyun-cli-devops` 插件。它有 `codeup-*`、`projex-*`、`flow-*`、`test-hub-*` 模块。旧 `devops/2021-06-25` 接口与新版 PAT / `/oapi/v1` 体系不能混用。

已知 CLI 缺口按 Skill 的[固定调用规则](../skills/codeup/references/access.md#固定调用规则)处理；少量 API 脚本与 CLI 共用本机凭据来源，不增加一套登录或完整 CLI。

已接入 [官方 MCP](https://github.com/aliyun/alibabacloud-devops-mcp-server) 时可以直接复用；按本次操作核对工具覆盖，不假定其与 CLI 完全等价。[官方通用 Skill](https://github.com/aliyun/alibabacloud-aiops-skills/tree/master/skills/developertools/rdc/alibabacloud-devops) 也可作为工具参考，本 Skill 专注工作流。

## 第三方 CLI

核查 [JilunSun7274/codeup-cli](https://github.com/JilunSun7274/codeup-cli/tree/f80472ebac3fc38482a415ce8f4d15fbd61ccae4)（v0.6.0）时，其命令集中在 Codeup 的 auth/repo/branch/pr，未覆盖 ProjeX、Flow、Testhub，创建 PR 的接口未暴露 `workItemIds`。它可用于已验证的辅助操作，不能承担完整需求交付链路。后续版本需重新核查。

不全局替换 `gh`，也不通过伪装 GitHub 域名接入云效。需要原生界面的应用应实现独立 Codeup Provider，并为 ProjeX 保留工作项模型；支持程度通过 capability 明示。
