# `scripts/ingest.py` 详解

这个 CLI 入口手动重建知识索引。文件开头从自身位置计算 PROJECT_ROOT 并加入 `sys.path`，保证用户直接执行 `python scripts/ingest.py` 时也能导入根目录的 app 包；否则 Python 默认只搜索 scripts 目录。`main()` 配置日志、创建统一服务、调用 `rag.ingest()`，最后打印文件数、解析单元数与分块数。三者能帮助发现异常：例如有 5 个文件却只有 4 个被解析，说明某格式可能为空或失败。

脚本复用应用服务配置，不复制 Loader 参数。生产应将重建变成有权限的后台任务，先写新索引，再原子切换别名，避免查询同时看到半成品。
