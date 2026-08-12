# `app/memory/store.py` 详解

`InMemoryConversationStore` 保存短期多轮对话。数据结构是 `session_id -> LangChain Message 列表`，因此不同浏览器会话不会混在一起。

`get_messages()` 返回列表副本，调用方不能绕过锁直接修改内部状态。`add_turn()` 一次写入 HumanMessage 和 AIMessage，随后 `_prune()`。裁剪先保留最后 max_messages 条，再检查总字符数；如果一条特别长，继续从最旧端移除。双重限制比单独限制轮数安全，因为 6 条消息也可能各有几万字。`clear()` 支持用户新建对话或隐私删除。

`RLock` 只保护单进程线程，并不能让多个 Uvicorn worker 共享状态。生产应换 Redis/PostgreSQL，键至少包含 tenant_id、user_id、session_id，增加 TTL、加密、导出/删除能力。更长历史可由单独摘要模型压缩，但摘要必须标记是历史概括，不能混成知识库事实。
