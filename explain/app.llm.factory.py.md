# `app/llm/factory.py` 详解

模型工厂隔离供应商 SDK。业务代码只依赖 LangChain 的 `BaseChatModel`，以后增加 Azure OpenAI、Anthropic 或企业本地模型时，不必改 Agent 路由。

`build_chat_model(settings)` 在演示模式返回 `None`。这不是偷偷伪装成 LLM，而是显式告诉上层走确定性演示路径。非演示模式目前只注册 OpenAI；未知 provider 主动失败，防止配置写错后静默回退。函数从环境变量读密钥，组装模型、温度和可选 base_url，再创建 `ChatOpenAI`。

温度 0.1 适合企业问答，因为任务重在忠实与稳定，不需要创意发散。模型名不硬编码在业务中，便于按成本与能力切换。常见问题包括把 key 写进源码、对模型对象提前 `bind_tools` 后又交给 `create_agent` 的结构化输出、以及没有给网络调用设置组织级重试与超时。后两项可在生产工厂中统一扩展。
