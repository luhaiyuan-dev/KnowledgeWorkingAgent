# `app/prompts/manager.py` 详解

`PromptManager` 把系统 Prompt 从 Python 代码移到 `configs/prompts.yaml`。产品或安全人员可以审阅提示词，Git diff 也能独立显示 Prompt 修改。

构造函数接受可选路径，便于测试或多租户加载不同 Prompt；默认使用项目根目录。`get(name)` 对缺失键主动抛 `KeyError`，比返回空字符串后让模型行为变得不可预测更安全。`format(name, **values)` 使用 Python 字符串格式化注入 history、context 和 question。

需要注意：知识库文本也是不可信输入，不能让其中的“忽略系统指令”获得系统级权限；系统 Prompt 始终放 SystemMessage，检索内容只放用户任务上下文。复杂生产项目可引入 Prompt 版本号、A/B 实验和模板变量白名单。
