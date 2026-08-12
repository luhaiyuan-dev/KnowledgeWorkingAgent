# `tests/test_loader.py` 详解

第一个用例读取真实五份样例，断言 PDF、DOCX、XLSX、TXT、MD 都产生非空 Document。这是比 mock 更有价值的格式集成测试。第二个用例在临时目录制造知识根和外部 secret，确认绝对路径越界也会抛 PermissionError；它验证安全边界而非只验证正常功能。
