# `app/core/schemas.py` 详解

本文件是系统的数据合同中心。Pydantic 模型同时服务于 FastAPI 请求校验、Agent 内部传递和最终 JSON 序列化，比在不同层随意传字典更容易发现字段拼错与类型错误。

`RouteName` 限制为 `chat/knowledge/tools/combo`。`UserContext` 保存可信身份映射后的用户信息；演示默认角色是 employee，但生产环境绝不能相信浏览器自己提交的角色。`ChatRequest` 描述消息、会话、手动模式、用户和已确认动作。`RouteDecision` 是路由器输出，`tools` 只列候选工具，不表示已经通过权限。

`Citation` 保存来源编号、文件、位置、片段和 0—1 得分。位置刻意使用字符串，因为 PDF 是页码、Excel 是工作表、TXT 是分块，强行统一成 page 会丢语义。`TraceStep` 用 completed/skipped/failed 展示执行过程。`AgentResponse` 是 UI/API 统一返回，包含自然语言、引用、工具、轨迹、请求 ID 和可选结构化数据。

`StructuredAgentAnswer` 是真实 LangChain Agent 的结构化输出 schema。模型必须给出 answer、used_tools 和 key_points，减少前端解析自由文本。`RetrievedChunk` 同时保留向量分和重排分，方便离线评估。

常见问题：新增字段时要给向后兼容默认值；外部输入字段要设置长度与数值范围；不要把 ORM、HTTP 和 Agent 状态各自复制成不一致模型。面试可回答“schema 是跨层契约，也是运行时防线”。
