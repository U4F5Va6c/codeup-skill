# Markdown 与富文本

让工作项、MR 和评论具有接近 GitHub 的可读性与链接体验。本 Skill 负责平台格式适配；内容、章节、措辞、详略和模板由当前流程 Skill（如 to-spec、to-tickets、pr、review）、用户要求及项目约定决定。转换格式时保留原有语义与结构。

## 按写入入口选择格式

以下于 2026-10-11 使用中心版、`aliyun-cli-devops 0.9.1` 及新版 PAT API 在隔离测试项目写入、回读并核对实际页面；其他版本先看当前命令帮助与 schema。

| 入口 | 写入方式与实测结果 |
|---|---|
| ProjeX 工作项描述 | 创建用 `--description` 传 Markdown，并显式设 `--format-type MARKDOWN`；更新的 `--biz-body` 同时包含 `description` 与 `formatType: "MARKDOWN"`。本轮创建后的标题、粗斜体、列表、链接、代码和表格正常渲染；复选框有下述显示限制。 |
| ProjeX 工作项评论：原生 Markdown | 新版 API 显式传 `formatType: "MARKDOWN"`，回读为 `contentFormat: "MARKDOWN"`；标题、粗斜体、列表、命名链接、代码和表格正常渲染；复选框有下述显示限制。 |
| ProjeX 工作项评论：当前 CLI | `projex-create-workitem-comment --content` 未暴露格式选项，回读为 `contentFormat: "RICHTEXT"`。直接传 Markdown 会显示原始符号；传 HTML 可正常渲染标题、粗斜体、列表、命名链接、行内代码、代码块和表格。 |
| Codeup MR 描述 | `description` 可使用 Markdown；已核对测试 MR 的标题、列表、命名链接和代码块正常渲染。 |
| Codeup MR 评论 | `codeup-create-change-request-comment --content` 可直接传 Markdown；标题、粗斜体、列表、命名链接、代码、表格和复选框正常渲染。已解决评论的折叠摘要可能显示原始语法，展开后再判断。 |

普通链接使用真实资源 URL，以标题、工作项编号或短 SHA 为链接文字均可；语法示例为 `[文字](https://example.com)` 或 `<a href="https://example.com">文字</a>`，发布时替换为真实目标。链接不会自动建立父子、阻塞或 MR 关联，也不能据此假定支持 GitHub 的 `#123` 自动引用。

## ProjeX 评论：优先原生 Markdown

为保留 Markdown 源文和接近 GitHub 的编辑体验，优先使用支持指定格式的入口。中心版已验证：

```http
POST /oapi/v1/projex/organizations/{organizationId}/workitems/{id}/comments
Content-Type: application/json

{"content":"## 标题\n\n**内容**","formatType":"MARKDOWN"}
```

写入字段是 `formatType`，回读字段是 `contentFormat`。使用 [本机凭据入口](access.md#按执行环境选择凭据入口) 注入同一 PAT，由请求进程从环境变量设置 `x-yunxiao-token` 请求头；不将令牌放进命令参数或日志，也无需旧版 AccessKey。当前 API 文档和 CLI 帮助未列出此写入字段，但官方 MCP 源码已传递该字段，上述请求已通过真实 API 与页面验证。

`aliyun-cli-devops 0.9.1` 没有对应评论格式参数，不能直接添加 `--format-type`。可直接调用上述新版 API；使用 MCP 时先确认实际工具 schema 暴露 `formatType`，再设为 `MARKDOWN`。本轮验证了 MCP 对应的 REST 请求，未单独运行 MCP 客户端。网页评论编辑器也提供“切换到Markdown编辑器”入口，已检查可切换。

## ProjeX 评论的 CLI 兼容写法

将已经确定的内容表示为 HTML，交给同一 CLI 的 `--content`；无需为此更换凭据或工具。实测可用的基础元素为 `h2`、`p`、`strong`、`em`、`ul/li`、`a`、`code`、`pre/code`、`table/tr/th/td`。正文文字中的 `<`、`>`、`&` 以及属性值按 HTML 规则转义，尤其要保留代码原文。

多行内容先写临时文件，用带引号的参数保留换行与特殊字符。下例仅展示原生命令参数；执行时仍须通过 [本机凭据入口](access.md#按执行环境选择凭据入口) 注入：

```sh
aliyun devops projex-create-workitem-comment \
  --id <工作项API-ID> --content "$(cat comment.html)"
```

HTML 是保持当前 CLI 命令不变时的兼容方案；CLI 缺少格式选项不代表 ProjeX 评论不支持 Markdown。

## 验证范围

首次使用某入口或更换工具版本时，在已授权测试资源写入代表实际内容的小样，回读内容与格式，再检查展开后的页面和链接目标。HTTP 成功只证明请求被接受；只有实际页面正确渲染才算格式验证通过。同一已验证入口的日常操作无需反复创建测试评论。

Codeup 的 Markdown 评论复选框正常显示且只读。ProjeX 正文与 Markdown 评论虽解析出正确的只读勾选状态，但当前页面将复选框排到预览区左侧并裁剪，截图只显示清单文字；不能将 DOM 解析成功等同于任务清单显示正常。本轮未验证 ProjeX HTML 评论的复选框、图片或其他 GitHub 扩展语法；需要这些能力时针对所用入口实测，不把工作项描述的支持范围套用到评论。Flow、Testhub 等其他文本字段同样按各自 schema 验证。

## 来源

- [ProjeX 描述编辑器](https://help.aliyun.com/zh/yunxiao/user-guide/new-demand)
- [创建工作项](https://help.aliyun.com/zh/yunxiao/developer-reference/createworkitem) / [更新工作项](https://help.aliyun.com/zh/yunxiao/developer-reference/updateworkitem)
- [创建工作项评论](https://help.aliyun.com/zh/yunxiao/developer-reference/createworkitemcomment) / [读取评论格式](https://help.aliyun.com/zh/yunxiao/developer-reference/listworkitemcomments)
- [Codeup 创建评论](https://help.aliyun.com/zh/yunxiao/developer-reference/createchangerequestcomment) / [合并请求编辑与评论](https://help.aliyun.com/zh/yunxiao/user-guide/consolidation-request-capability-overview/)
- [官方 MCP 评论实现](https://github.com/aliyun/alibabacloud-devops-mcp-server/blob/master/operations/projex/workitem.ts)
