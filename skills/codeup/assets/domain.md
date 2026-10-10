# Domain docs

默认 single-context：仓库根 `GLOSSARY.md` 与 `docs/adr/`。

探索代码前读取相关领域词汇及 ADR；如果已有 `GLOSSARY-MAP.md`，按映射读取相关上下文。相关文件不存在时继续工作，不预先创建空文件。

工作项、规格和 MR 使用领域词汇表的用词。发现与 ADR 冲突时明确指出具体决策，让用户判断是否重议。`domain-modeling` 在实际厘清术语或决策时维护这些文档。
