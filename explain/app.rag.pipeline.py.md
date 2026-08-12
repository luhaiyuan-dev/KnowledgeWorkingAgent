# `app/rag/pipeline.py` 详解

`RagPipeline` 是 RAG 子系统的门面，把 Loader、Splitter、Embedding、VectorStore、Reranker 串起来。Agent 不需要知道 PDF 怎么读或向量怎么算，只调用 ingest、retrieve 与 citation 构造。

构造函数从 Settings 解析知识目录、索引路径和切分参数。`ingest()` 完成加载、切分、替换索引，并返回文件/解析单元/分块数量；这三个数不同，例如 PDF 每页一个解析单元。`ensure_index()` 只在空索引时自动入库，避免每次 Streamlit 重跑都重新计算。

`retrieve(query, allowed_scopes)` 先向量召回 top_k，再混合重排到 top_n。权限范围作为检索参数传入，而不是拿到结果后在 UI 隐藏。`build_context_and_citations()` 给结果分配 S1、S2，构造供模型读取的上下文和供 API/UI 渲染的 Citation。`_focused_excerpt()` 以查询双字词给分块内的滑动窗口打分，展示最贴近问题的 260 字，而不是机械展示分块开头；完整 chunk 仍进入模型上下文。`_format_location()` 优先页码，其次工作表，最后分块。

`load_named_file()` 是工具读取文件的复用入口。生产化时可增加入库清单、内容哈希、删除传播、版本号、索引别名切换和后台任务，避免重建期间服务抖动。
