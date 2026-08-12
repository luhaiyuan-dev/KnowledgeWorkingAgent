# `app/tools/registry.py` 详解

`ToolRegistry` 把工具列表转成 name 到对象的字典，负责注册查找和权限裁剪。`names()` 排序返回，便于 UI 或诊断；`get()` 对未知工具抛错，防止静默执行错误名称；`allowed_for_user()` 逐个问 PolicyEngine，最终只把允许工具交给 LangChain Agent。

这一点很关键：模型看不见的工具就无法调用。不要把所有工具都暴露给模型，再期待系统 Prompt 说“访客不要调用数据查询”就安全。生产可在注册时检查重名、版本、风险等级、超时和审计 metadata。
