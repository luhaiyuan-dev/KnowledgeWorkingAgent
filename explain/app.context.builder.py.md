# `app/context/builder.py` 详解

Context 不等于 Memory：Memory 是存下来的历史，Context 是本次请求实际送进模型的有限信息。`ContextBuilder` 负责把两者分开。

`format_history()` 把 LangChain Human/AI Message 转成明确的“用户/助手”行，并从字符串尾部保留不超过 max_characters 的最近内容。保留尾部符合对话时近因更重要的经验。生产可改成按 token 预算，因为不同模型 tokenization 不同。

`build_system_context()` 注入当前用户 ID、显示名、角色和部门，让模型能解释权限相关情况。但真正授权仍由 PolicyEngine 代码执行；模型看到“管理员”绝不等于获得管理员权限。这是面试里常问的“LLM 软约束与后端硬约束”区别。
