# 配置与界面非 Python 文件说明

## `.env.example`

只列变量名和安全空值，供复制为被 Git 忽略的 `.env`。`DEMO_MODE=true` 保证第一次启动零密钥；真实密钥不得写入示例。

## `configs/settings.yaml`

按 app、llm、embedding、rag、memory、security、web_search 分区。路径均以项目根为基准。切分、召回和窗口参数集中在此处，便于实验而不改代码。

## `configs/permissions.yaml`

定义 guest、employee、admin 的工具和文档范围，以及高风险工具列表。通配符只由 PolicyEngine 解释。生产修改必须走安全评审。

## `configs/prompts.yaml`

路由、Agent 和 RAG Prompt 独立版本管理。花括号变量由 PromptManager 注入；知识上下文永远不能升级成 SystemMessage。

## `ui/styles.css`

颜色使用设计稿抽取 token：真白背景、深海军蓝文字、蓝色强调、冷灰侧栏。CSS 只改变视觉，不隐藏安全信息或替代后端权限。HTML 来源内容在 Python 中 escape 后才进入自定义来源块。

## `.streamlit/config.toml`

锁定 Streamlit 原生控件的主蓝、真白背景、冷灰侧栏、深蓝文字和中等圆角，并将开发工具条设为 minimal。CSS 进一步隐藏仅对开发者有用的 toolbar，使本地产品界面与概念设计一致；这不隐藏错误或权限提示。

## 依赖文件

`requirements.txt` 固定运行版本，避免教学代码因上游大版本漂移突然失效；`requirements-dev.txt` 在其上添加 pytest、覆盖率和 Ruff。`pyproject.toml` 统一 Python 范围、测试路径和 lint 规则。
