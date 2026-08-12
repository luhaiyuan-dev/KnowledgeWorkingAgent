# `app/rag/loader.py` 详解

加载器的任务是把异构文件统一转成 LangChain `Document(page_content, metadata)`。支持集合明确为 PDF、DOCX、XLSX、TXT 和 Markdown；未知格式立即拒绝。

`EnterpriseDocumentLoader.__init__` 保存解析后的允许根目录。`load_directory()` 递归扫描并按路径排序，排序保证同一份材料每次生成的 chunk 编号稳定。`load_file()` 先调用 `_resolve_safe_path()`：相对路径只能落在知识库根目录，绝对路径也必须是其子路径，从而阻止 `../../secret.txt`。这道路径防线必须在真正打开文件之前。

`_load_text()` 保留原始 Markdown/TXT。`_load_pdf()` 用 pypdf 逐页提取并把 page 写入 metadata；扫描件没有文字时会跳过，因此生产中要在入库前加 OCR。`_load_word()` 按段落读取，也把表格按 `|` 展开，避免只读 paragraphs 漏掉合同表格。DOCX 没有可靠“页面”概念，因为页码由字体和渲染器决定，所以不伪造页码。`_load_excel()` 逐工作表读取，第一行做表头，后续每行转成“字段: 值”，并保存 sheet 名称。

为什么不直接用一堆社区 Loader？这里用底层库是为了让初学者看见真实格式差异和 metadata 设计，也减少版本漂移。生产需补充密码文件、宏文件、超大工作簿流式限制、公式与隐藏行策略、OCR、恶意压缩包及 MIME 检查。
