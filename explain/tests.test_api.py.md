# `tests/test_api.py` 详解

FastAPI `TestClient` 在 lifespan 内启动服务。健康用例验证 200 和 ok；聊天用例提交最小 JSON，验证响应有 answer。随后通过 `runpy.run_path` 按直接文件方式加载 Streamlit 入口，专门防止 `ui/app.py` 遮蔽根 app 包；再用 Streamlit 官方 `AppTest` 真正执行页面脚本，要求没有运行时 exception 且页面标题正确，因此头像、Widget 参数等 UI API 错误也会进入 CI。接口测试关注 HTTP 契约，具体 RAG 正确性由服务测试负责，从而避免每层重复同一断言。
