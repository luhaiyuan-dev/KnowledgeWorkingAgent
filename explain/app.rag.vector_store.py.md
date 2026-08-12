# `app/rag/vector_store.py` 详解

`LocalVectorStore` 是一个透明的教学型向量库：文档与向量保存在 JSON，检索用 NumPy 矩阵乘法。它让学习者不安装 Docker 或数据库也能理解“写入—持久化—召回”的全流程。

构造函数接收 Embedding 与索引路径；文件存在就 `load()`。`replace_documents()` 批量计算向量、转 float32、逐行归一化，然后在锁内整体替换并持久化。整体替换比增量更新简单，适合五个样例文件；大规模生产要做文档哈希和增量 upsert。

`similarity_search_with_score()` 先嵌入查询并归一化，用 `matrix @ query` 一次得到所有余弦分。随后在返回前检查 access_scope，避免越权文档进入候选。原余弦范围 -1 到 1，被线性映射到 0—1 便于 UI 展示。`persist()` 先写 `.tmp` 再原子 replace，降低进程中断留下半个 JSON 的概率。`RLock` 防止同进程重建索引与查询同时修改列表。

限制很明确：JSON 体积大、全量扫描是 O(N)、多进程锁无效、没有备份和数据库级过滤。生产可替换为 pgvector、Milvus、Qdrant 或 Elasticsearch，但应保留当前接口和“过滤必须进入检索层”的安全原则。
