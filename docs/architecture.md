# 架构说明与设计取舍

## 分层原则

入口层只有 `ui/` 和 `api/`，不直接写检索或工具业务；它们调用 `EnterpriseAgentService`。服务层负责组织流程，领域能力分别放在 `rag/`、`tools/`、`memory/`、`auth/` 和 `security/`。配置与数据结构位于 `core/`，从而避免模块互相导入 UI。

## 为什么没有一开始使用 LangGraph 自定义图

LangChain 1.x 的 `create_agent` 本身就是基于 LangGraph 的生产级循环，已经处理工具调用、错误反馈和终止。当前需求优先“清晰、易学习、不过度复杂”，所以业务四路路由用普通 Python 类表达，工具循环交给 `create_agent`。当未来需要审批中断、长任务恢复、并行分支或持久化检查点时，再把 `EnterpriseAgentService` 的每个阶段迁移为 LangGraph 节点。

## 演示模式与生产模式

演示模式不是伪造返回：文档解析、切分、Embedding、向量检索、重排、权限、安全、工具和引用都真实运行，仅开放式语言归纳用透明模板代替。这个边界让项目在没有密钥时仍可验证核心 RAG。生产模式使用 ChatOpenAI 与 `create_agent(response_format=StructuredAgentAnswer)`。

## 依赖方向

```text
UI / API -> Agent Service -> Router / RAG / Tools / Memory
                         -> Auth / Security / Context
RAG -> Loader -> Splitter -> Embeddings -> VectorStore -> Reranker
所有层 -> core.schemas / core.config
```

下层不得导入 Streamlit 或 FastAPI。这样以后替换为企业 IM、桌面客户端或批处理入口时，业务模块无需改写。
