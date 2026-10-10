# Markdown 与富文本

让工作项、MR 和评论具有接近 GitHub 的可读性与链接体验。本 Skill 负责平台格式适配；内容、章节、措辞、详略和模板由当前流程 Skill（如 to-spec、to-tickets、pr、review）、用户要求及项目约定决定。转换格式时保留原有语义与结构。

## 按写入入口选择格式

以下于 2026-10-11 使用中心版、`aliyun-cli-devops 0.9.1` 在隔离测试项目写入、回读并核对实际页面；其他版本先看当前命令帮助与 schema。

| 入口 | 写入方式与实测结果 |
|---|---|
| ProjeX 工作项描述 | 创建用 `--description` 传 Markdown，并显式设 `--format-type MARKDOWN`；更新的 `--biz-body` 同时包含 `description` 与 `formatType: "MARKDOWN"`。本轮创建后的标题、粗斜体、列表、链接、代码、表格和复选框正常渲染。 |
| ProjeX 工作项评论 | `projex-create-workitem-comment --content` 未暴露格式选项，回读为 `contentFormat: "RICHTEXT"`。直接传 Markdown 会显示原始符号；传 HTML 可正常渲染标题、粗斜体、列表、命名链接、行内代码、代码块和表格。 |
| Codeup MR 描述 | `description` 可使用 Markdown；已核对测试 MR 的标题、列表、命名链接和代码块正常渲染。 |
| Codeup MR 评论 | `codeup-create-change-request-comment --content` 可直接传 Markdown；标题、粗斜体、列表、命名链接、代码、表格和复选框正常渲染。已解决评论的折叠摘要可能显示原始语法，展开后再判断。 |

普通链接使用真实资源 URL，以标题、工作项编号或短 SHA 为链接文字均可；语法示例为 `[文字](https://example.com)` 或 `<a href="https://example.com">文字</a>`，发布时替换为真实目标。链接不会自动建立父子、阻塞或 MR 关联，也不能据此假定支持 GitHub 的 `#123` 自动引用。

## ProjeX 评论的 CLI 写法

将已经确定的内容表示为 HTML，交给同一 CLI 的 `--content`；无需为此更换凭据或工具。实测可用的基础元素为 `h2`、`p`、`strong`、`em`、`ul/li`、`a`、`code`、`pre/code`、`table/tr/th/td`。正文文字中的 `<`、`>`、`&` 以及属性值按 HTML 规则转义，尤其要保留代码原文。

多行内容先写临时文件，用带引号的参数保留换行与特殊字符。下例仅展示原生命令参数；执行时仍须通过 [本机凭据入口](access.md#按执行环境选择凭据入口) 注入：

```sh
aliyun devops projex-create-workitem-comment \
  --id <工作项API-ID> --content "$(cat comment.html)"
```

HTML 是当前 CLI 评论入口的已验证路径。官方 MCP 源码另有评论 `formatType` 参数，但不等于已安装 CLI 支持它，也不证明当前服务端的 Markdown 评论渲染已通过验证。需要换用其他路径时重新核对实际 schema 和页面，避免将旧版 API 参数拼进新版命令。

## 验证范围

首次使用某入口或更换工具版本时，在已授权测试资源写入代表实际内容的小样，回读内容与格式，再检查展开后的页面和链接目标。HTTP 成功只证明请求被接受；只有实际页面正确渲染才算格式验证通过。同一已验证入口的日常操作无需反复创建测试评论。

本轮未验证 ProjeX HTML 评论的复选框、图片或 GitHub 扩展语法；Codeup 评论中的 Markdown 复选框为只读展示。需要这些能力时针对所用入口实测，不把工作项描述的支持范围套用到评论。Flow、Testhub 等其他文本字段同样按各自 schema 验证。

## 来源

- [ProjeX 描述编辑器](https://help.aliyun.com/zh/yunxiao/user-guide/new-demand)
- [创建工作项](https://help.aliyun.com/zh/yunxiao/developer-reference/createworkitem) / [更新工作项](https://help.aliyun.com/zh/yunxiao/developer-reference/updateworkitem)
- [创建工作项评论](https://help.aliyun.com/zh/yunxiao/developer-reference/createworkitemcomment) / [读取评论格式](https://help.aliyun.com/zh/yunxiao/developer-reference/listworkitemcomments)
- [Codeup 创建评论](https://help.aliyun.com/zh/yunxiao/developer-reference/createchangerequestcomment) / [合并请求编辑与评论](https://help.aliyun.com/zh/yunxiao/user-guide/consolidation-request-capability-overview/)
- [官方 MCP 评论实现](https://github.com/aliyun/alibabacloud-devops-mcp-server/blob/master/operations/projex/workitem.ts)
