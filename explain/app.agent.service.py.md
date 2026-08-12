# `app/agent/service.py` 详解

这是项目的应用服务中枢。构造函数只组装依赖：设置、Prompt、模型、RAG、Memory、Context、Policy、Guardrails 和 Router。UI 与 API 都调用同一个服务，避免两套行为。

`chat()` 为请求生成 UUID，做输入安全检查，确保索引存在，执行路由并建立 trace。异常被记录并转成用户可理解的失败响应，最后保存一轮 Memory、脱敏记录日志。`_execute_route()` 是四路调度：chat 调 `_run_normal_chat()`；knowledge 检索并 `_answer_with_knowledge()`；tools/combo 先按 Policy 构建允许工具，再选择路由候选，最后进入演示执行或真实 Agent。

演示模式中 `_run_normal_chat()` 明示能力边界；知识回答调用 `_best_sentence()`，用查询双字词给证据中的句子打分，“哪些/哪几种”类问题还给枚举型句子加分，只把首条证据最相关的事实句放进正文并标 S 编号，全部证据仍留在来源区，避免把检索片段堆成难读长文。真实模式把历史、系统 Prompt 和知识上下文交给模型。`_run_langchain_agent()` 使用 LangChain 1.x `create_agent`，传入过滤后的工具和 `StructuredAgentAnswer`，并用 recursion_limit 限制循环。它不使用旧 `AgentExecutor` 或已弃用 `ConversationChain`。

`_run_demo_tools()` 根据明确路由执行确定性工具，并把结果作为 JSON 展示；`_demo_tool_arguments()` 只做有限参数提取，不声称拥有 LLM 理解。`_find_mentioned_file()` 只枚举知识根目录；`_extract_quoted_text()` 处理中英文引号；`_content_to_text()` 兼容模型多段内容。

潜在问题：当前 Agent 每次请求重新 create，适合教学但可按“角色工具集合+模型”缓存；服务对象内 Memory 只适合单实例；异常答复不应向生产用户暴露内部细节；真实工具调用的 used_tools 最好从消息轨迹审计而非完全相信模型结构化声明。面试可把该类解释为 orchestration/application service，而不是把所有算法写成一个巨型 Agent。
