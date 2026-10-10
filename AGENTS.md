# 维护约定

- 用中文沟通。提交格式为 `{type}-{中文模块}-{中文描述}[-{关联项}]`。
- `skills/codeup/` 是唯一技能源；不编辑 Dotfiles 快照或 Agent 安装副本。
- 入口只保留任务路由与共同规则，细节放 references；示例不包含真实租户信息。
- 涉及云效行为时查当前官方 API/工具 schema，不把旧版 API 参数套到新版 CLI。
- 运行 `python3 -m unittest discover -s tests -v`；结构检查不能替代真实 API 验证。
- 维护流程见 CONTRIBUTING.md。没有明确请求时不发布评论、创建 PR 或执行云效写操作。
