# `api/main.py` 详解

FastAPI 是机器调用入口。模块加载设置、日志与单例 Agent 服务。`lifespan()` 在服务启动时确保索引存在，替代旧式 startup decorator，并为以后增加连接关闭留下位置。

`health_check()` 返回服务状态、演示模式和分块数；健康检查不调用 LLM，避免外部依赖抖动导致容器被反复重启。`chat()` 接收经过 Pydantic 校验的 ChatRequest，返回 AgentResponse；意外异常转 HTTP 500。`reindex_knowledge_base()` 触发全量索引，生产必须加管理员权限并改为后台任务。`clear_session()` 清除指定短期记忆。

FastAPI 自动在 `/docs` 生成 OpenAPI UI。生产还要加认证、中间件 request_id、CORS 白名单、限流、超时、幂等和统一错误码；不能允许任何用户调用 reindex 或任意清理他人会话。
