# `app/auth/policy.py` 详解

`PolicyEngine` 读取 `permissions.yaml`，实现简化 RBAC。角色决定允许的工具和文档范围。权限写在配置而不是散落在每个工具的 if 语句里，便于审计和扩展。

`allowed_tools()` 合并用户所有角色的工具集合；`allowed_document_scopes()` 同理。`can_use_tool()` 支持管理员的通配符 `*`。`is_high_risk_tool()` 标记会改变外部状态的工具，配合人工确认接口。

当前演示策略是“多角色权限取并集”。生产要先决定并集、优先拒绝或属性策略，还要加入租户、资源所有者、部门层级、文档密级和时间条件。最关键的是 UserContext 必须由服务端验证后的 SSO Token 构造，不能使用用户可篡改的 JSON。Agent 只能看到过滤后的工具列表，这比让模型自行决定“我有没有权限”可靠。
