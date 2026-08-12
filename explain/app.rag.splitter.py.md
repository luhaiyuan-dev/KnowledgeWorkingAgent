# `app/rag/splitter.py` 详解

切分器决定“向量库中一个可召回单元有多大”。太大时一个向量混合多个主题、送给 LLM 成本高；太小时语义破碎、需要更多结果才能拼回事实。

`CHINESE_SEPARATORS` 从段落和换行开始，再尝试中文句号、问号、分号、逗号，之后才是英文标点、空格和单字符。这是一种结构感知的字符递归切分：不是简单每 800 字一刀，也不是需要额外模型的语义切分。对中文企业文档，它在效果、速度、可解释性之间平衡较好。

`EnterpriseTextSplitter.__init__` 检查 overlap 必须小于 size，否则切分器可能无法前进。`length_function=len` 表示按 Python 字符数量而非 token；中文字符与 token 并非 1:1，但长度稳定、无需绑定某个模型 tokenizer。`split_documents()` 调用 LangChain 官方实现，并给每个结果写全局 chunk_index。

默认 800/120 约 15% 重叠，能覆盖跨句边界。面试时不要说这是固定最佳值，应说明要用问答集测 recall@k、忠实度、延迟和 token 成本。Markdown 规模变大时可先按标题结构切，再做递归子切分；法律合同可增加条款编号分隔符。
