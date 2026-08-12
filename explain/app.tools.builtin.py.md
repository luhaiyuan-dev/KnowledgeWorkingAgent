# `app/tools/builtin.py` 详解

这个文件定义六个 LangChain 工具及其输入 schema。Pydantic schema 会在执行前检查字段、范围和类型，工具 docstring/description 则告诉模型什么时候调用。

`SafeCalculator` 使用 Python AST 解析表达式。`calculate()` 限长、解析为 eval 模式、递归求值、拒绝无穷结果。`_evaluate_node()` 只允许数值常量、白名单二元/一元运算，指数绝对值最多 100。不能用 `eval()`，即使先做正则也可能被构造绕过。

`build_builtin_tools()` 闭包捕获 RAG、配置和用户允许的文档范围：

- `knowledge_base_search` 调用 RAG 并返回上下文与结构化引用。
- `file_reader` 复用安全 Loader，限制最大字符数。
- `calculator` 返回表达式与结果。
- `data_query` 只允许知识库中的 XLSX，选择工作表、按序列化行包含条件过滤并限制 100 行。它不是任意 SQL，从而避免注入。
- `web_search` 只有配置 Tavily key 才联网，设置超时并返回标题、URL、摘要。工具结果仍是不可信第三方内容。
- `document_analysis` 提取长度、标题和关键词命中段落，是无 LLM 也能跑的基础分析。

最后用 `StructuredTool.from_function` 注册名称、说明和 schema。生产中应把每个工具拆文件、加超时/重试/熔断/指标，并对返回数据做 DLP。工具名称变更会影响 Prompt 和权限配置，需要版本管理。
