# `ui/app.py` 详解

Streamlit 提供最少依赖的可运行 Web 对话界面。文件开头把项目根目录移动到 `sys.path` 第一位；这是因为直接执行 `ui/app.py` 时 `ui` 会优先，文件名 app.py 会遮蔽真正的 app 包。`get_service()` 使用 `st.cache_resource`，否则每次按钮交互都会重建模型与索引。`load_css()` 读取单独 CSS，保持布局代码清楚。`initialize_state()` 创建会话 UUID 和欢迎消息。

`render_sidebar()` 提供新建对话、自动/对话/知识/工具模式、演示角色与重建索引。新建时同时清服务 Memory 和前端消息。角色选择只是教学演示，生产必须由 SSO 固定。`render_header()` 渲染品牌与在线状态。`render_citations()` 对来自文档的文字先 `html.escape`，避免知识库内容注入 HTML；相关度只作排序提示，不等于答案置信度。`render_trace()` 折叠展示每个执行步骤。

`main()` 设置页面、确保索引、渲染历史，等待 `st.chat_input`，调用统一服务，再把答案、引用与轨迹写回 session_state。核心控件和文字都是代码原生元素，不是设计稿截图。

界面从完整三栏设计稿提炼为“侧栏+主消息流+消息下证据”，因为 Streamlit 的原生右固定栏不稳定，且在移动端会挤压；折叠来源保持同一信息层级。生产前可增加流式 token、文件上传入库审批、反馈按钮和真实身份展示。
