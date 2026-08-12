# `app/security/guardrails.py` 详解

安全护栏提供三类硬防线：输入检查、日志 PII 脱敏和允许目录解析。`GuardrailResult` 明确返回 allowed、清洗文本和警告。

`inspect_input()` 去除首尾空白、拒绝空输入和超长输入，再用正则识别常见中英文 Prompt Injection。默认只告警不拦截，因为用户可能在讨论安全案例；生产可开启 block。仅靠关键词绝不等于完整注入防护，真正边界来自不把知识文本放 SystemMessage、工具权限过滤、路径限制和高风险确认。

`mask_pii()` 演示手机号、邮箱、身份证号脱敏，调用发生在写日志前。生产 DLP 需要覆盖姓名、地址、客户号、银行卡和业务自定义实体。`resolve_allowed_path()` 把相对路径固定到根目录、resolve 掉 `..` 和符号链接，再确认候选仍在根目录内，是文件工具抵御路径穿越的关键。

常见错误是只检查字符串是否以某路径开头（`C:\data2` 会冒充 `C:\data`），或先打开文件再检查。本项目用 Path parents 做结构判断。
