# Futu Personal

个人 Codex 插件，基于 FutunnOpen/futu-agent-plugin 的 a1cfd82087453e0089a11fedc45f36ea85039930。

- 产品范围：富途 MCP 发布的全部能力，包括行情、筛选、资讯、自选管理、账户查询、真实交易接口、模拟交易。订单草稿是附加工具，不替代交易接口。
- 对外只暴露 `skills/futu-personal/SKILL.md` 一个总路由 Skill；业务规则按需读取 `reference/workflow-*.md`，参数参考集中在同一 `reference/` 目录。整理结构时保留完整业务细节，不复制 WorkBuddy 中相同的参考文档。
- `.mcp.json` 不设置静态工具允许列表或禁用列表，保留服务端工具发现。OAuth 默认申请服务端元数据声明的 quote:read、quote:write、trade:read、trade:write、accid:*。
- 工具参数以当前服务端 schema 为准；上游参考文档用于解释业务含义。未在本地参考中出现的新工具不能被直接判为不支持。
- 开发验收区分工具注册、OAuth 授权和实际调用。开发或验证插件不授权发送真实证券交易请求；宿主安全规则仍适用。
- OAuth 在富途授权页面完成，不将账号密码、Token 或真实账户数据写入仓库。
- 保留上游 MIT 版权声明；同步上游时更新 README 的基线提交。
- 修改后运行 `python3 scripts/validate_plugin.py` 与 `python3 -m unittest discover -s tests`。
- 集成验收分为本地插件加载、全量工具发现、OAuth 权限与账户绑定、实际只读调用、写操作；未执行的阶段不写成已通过。
