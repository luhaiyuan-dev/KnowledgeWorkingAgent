# `app/observability/logging_config.py` 详解

企业 Agent 的错误跨越路由、检索、模型和工具，普通散乱 print 很难追踪。`JsonFormatter` 把每条日志变成一行 JSON，包含 UTC 时间、级别、logger、消息，以及可选 request_id 和 event。

`configure_logging()` 创建 logs 目录，读取 LOG_LEVEL，清空旧 handler，添加控制台与 `logs/agent.jsonl` 文件。清空 handler 对 Streamlit 尤其重要，否则脚本重跑会重复添加，导致一条事件打印多次。

业务层在写输入前调用 PII 脱敏，并为每个请求生成 UUID。生产还应增加延迟、模型 token、费用、检索命中、工具参数摘要、用户/租户审计键，但不得记录密钥、完整个人信息或敏感文档正文。日志文件写入适合单机学习；生产应发到集中日志平台并配置保留期限和访问控制。
