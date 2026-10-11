# Futu Personal

个人 Codex 插件，基于 FutunnOpen/futu-agent-plugin 的 a1cfd82087453e0089a11fedc45f36ea85039930。

- 产品范围：行情、筛选、资讯、授权账户查询、模拟交易、用户手动执行的实盘订单草稿。
- 不实现或调用真实下单、改单、撤单、风控确认、转账或其他资金操作；不能通过其他插件或直接 SDK/HTTP 替代。
- `.mcp.json` 的工具允许列表只收录已经核对的查询工具和模拟交易工具，新增工具先审查作用。
- OAuth 在富途授权页面完成，不将账号密码、Token 或真实账户数据写入仓库。
- 保留上游 MIT 版权声明；同步上游时更新 README 的基线提交。
- 修改后运行 `python3 scripts/validate_plugin.py` 与 `python3 -m unittest discover -s tests`。
- 集成验收分为本地插件加载、OAuth 授权、实际只读调用、模拟操作；未执行的阶段不写成已通过。
