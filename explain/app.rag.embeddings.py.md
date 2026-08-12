# `app/rag/embeddings.py` 详解

Embedding 把文本映射为向量，使语义或词形相近的内容距离更近。本文件提供三种策略并统一实现 LangChain `Embeddings` 接口。

`DeterministicHashEmbeddings` 是零网络教学后备。`embed_documents()` 批量调用 `_embed_text()`，`embed_query()` 保持同一算法。文本去空白、转小写后，`_make_tokens()` 生成单字和双字；每个 token 用 SHA-256 决定 384 维中的位置与正负号，最后做 L2 归一化。不能用 Python 内置 `hash()`，因为它跨进程默认随机，索引重启后会失效。归一化后点积就是余弦相似度。

Hash Embedding 擅长复现和精确词重叠，不理解真正同义词，因此只适合演示、单测和离线启动。`build_embeddings()` 根据 provider 返回 hash、OpenAI 或 HuggingFace。中文生产默认预留 `BAAI/bge-small-zh-v1.5`：它相对轻量，面向中英文检索，归一化输出便于余弦比较。HuggingFace 依赖较重，所以放在可选导入，默认安装不下载模型。

切换 Embedding 后必须重建整个索引；不同模型的维度和空间不可混用。生产还应记录模型版本、查询/文档前缀策略、批量大小、设备、缓存和数据出境要求。
