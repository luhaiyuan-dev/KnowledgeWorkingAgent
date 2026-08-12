# `tests/test_agent_service.py` 详解

`build_demo_service()` 深拷贝配置、强制演示模式并把索引放临时目录，保证测试无网络、无密钥、可重复。知识用例要求 route、citations 和 `[S1]` 同时存在；计算用例要求真正使用 calculator 并得到 274.3。它验证统一服务闭环而不是单个函数。
