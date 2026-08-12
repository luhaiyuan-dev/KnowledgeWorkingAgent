# `tests/test_router.py` 详解

在无 LLM 情况下分别验证公司问题走 knowledge，数学表达式走 tools 且选择 calculator。确定性路由测试便宜，适合 CI。随着关键词扩展，应增加 combo、普通对话、手动模式和误触发反例。
