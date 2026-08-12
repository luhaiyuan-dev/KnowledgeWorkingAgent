# `app/tools/enterprise.py` 详解

本文件预留 CRM、ERP、邮件和日历扩展，不提供会产生真实业务动作的假实现。`EnterpriseAction` 统一表示 operation、payload 和可选确认 token。

`EnterpriseToolAdapter` 是抽象基类。`run()` 在风险等级为 high 且 operation 不在 confirmed_actions 时，返回 `confirmation_required`，不会调用外部系统。通过后才进入抽象 `execute()`。四个具体 Adapter 只定义 name，并抛清楚的 NotImplementedError，提醒开发者在这里接企业 SDK。

实际接入不能只把风险确认做成一个前端复选框。应生成绑定用户、操作参数、资源、过期时间的一次性确认单；写操作带幂等键；使用最小权限服务账号；记录请求与外部响应；支持补偿或撤销。邮件“生成草稿”和“发送”、日历“查询空闲”和“创建会议”应拆成不同风险工具，便于精细授权。
