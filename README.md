# Futu Personal

个人 Codex 富途插件，当前版本 `0.2.0`。连接富途官方 MCP，提供行情、筛选、资讯、自选管理、账户查询、真实交易接口和模拟交易的完整接入。

`.mcp.json` 不设置 `enabled_tools` 或 `disabled_tools`。Codex 按富途 MCP 当前返回的 `tools/list` 发现全部工具，不用固定白名单裁剪能力。Skills 提供常见意图路由与参数参考；未列入路由的新工具以当前服务端 schema 为准。工具已注册、OAuth 已授权和实际操作成功是三个不同的验证结果。

基于 [FutunnOpen/futu-agent-plugin](https://github.com/FutunnOpen/futu-agent-plugin)，上游基线为 `a1cfd82087453e0089a11fedc45f36ea85039930`（2026-09-10）。保留 MIT License。本项目不是富途官方插件，也不包含富途 MCP 服务端实现。

## 安装和授权

需要本机 `codex` CLI。插件连接富途托管的 MCP，不需要安装 OpenD。

```bash
codex plugin marketplace add /Users/bytedance/github/futu-personal
codex plugin add futu-personal@futu-personal-local
codex mcp login futu-personal --scopes quote:read,quote:write,trade:read,trade:write
```

插件配置声明四类权限，登录命令也明确请求这四类权限。已有 `0.1.0` 的只读 OAuth 授权不会自动获得写权限，需要重新发起登录并由用户在富途页面选择和授予权限。最终可授予的范围取决于富途对当前客户端及账户的设置；不能把请求的 scope 当作已授予的 scope。

[富途官方认证文档](https://open.futunn.com/zh-cn/mcp-docs/authentication)说明了以下权限范围：

| Scope | 官方说明 |
|---|---|
| `quote:read` | 实时行情、历史 K 线等核心市场数据 |
| `quote:write` | 管理自选列表 |
| `trade:read` | 查询账户资产、持仓明细、历史订单 |
| `trade:write` | 执行下单、撤单操作 |

该文档没有逐一列出改单、风控确认和所有模拟工具的 scope 映射。具体要求以当前工具 schema、富途授权页和接口返回为准。

OAuth 由 Codex 客户端发起。修改本地插件名称和 Skills 不会把它变成 WorkBuddy 的 OAuth 客户端，WorkBuddy 已获得的权限也不会转给 Codex。登录、协议接受和最终授权由用户在页面完成；账号密码和 OAuth Token 不应粘贴到聊天或写入仓库。

安装或升级后，新建 Codex 聊天并选择 `@Futu Personal`。先检查工具加载，再查一只股票的报价，核对数据时间、币种和行情权限；账户查询时明确选择真实或模拟账户。

## 能力和操作规则

| 类别 | 接入能力 |
|---|---|
| 行情 | 报价、快照、K 线、盘口、分时、逐笔、市场状态、交易日历、板块 |
| 筛选与研究 | 股票筛选、期权、期货、窝轮、新闻、财务、资金流、股东、研报及公司行为 |
| 自选 | 分组与列表查询，`quote_modify_user_security` 的添加、删除和移出 |
| 账户 | 授权账户、资金、持仓、活跃及历史订单、订单详情、成交、最大可买卖 |
| 真实交易接口 | `trading_order_place`、`trading_order_replace`、`trading_order_cancel`、`trading_order_confirm` |
| 模拟交易 | 账户、资金、持仓、交易容量、历史订单查询，以及下单、改单、撤单 |
| 加密货币接口 | 资金、购买力、订单、成交，以及 `crypto_account_create_order`、`crypto_account_modify_order`、`crypto_account_cancel_order` |
| 新增工具 | 使用当前 MCP 返回的工具名称、描述和参数 schema，无需扩展本地白名单 |

交易及其他写操作需要先展示具体对象和参数，并按适用规则取得确认。返回成功不等于成交；订单状态需另行查询。写请求超时或结果不明确时，先核对结果，不自动重复提交。涉及风控二次确认时，使用本次响应的 `confirm_id` 并说明风控提示。

宿主的安全规则不会因交易接口已注册而改变；实际操作仍受当前平台规则和用户明确授权约束。

行情港股代码与真实订单交易所代码可能不同，例如 `HK.00700` 与 `SEHK.00700`。价格精度、数量单位、交易时段和支持的订单类型均需按对应工具核对，不把行情字段或模拟枚举直接套用到真实交易。

## 个人设置

`preferences.json` 是可提交的默认配置。账户和常用市场默认为空，不猜测用户的账户或偏好。

可用 `preferences.local.json` 覆盖个人偏好，该文件已被 Git 忽略。只保存偏好，不保存密码、OAuth Token 或真实账户数据。`query_account_id` 是查询偏好，不代表写操作授权；切换账户或真实/模拟环境时需重新核对。

查询默认最多 3 页、100 条；达到上限时说明截断，按需继续。报价注明市场、币种、数据时间和交易时段，保留接口精度。盈亏展示说明口径，不混合币种求和。

修改源码或配置后运行检查，再安装新版本：

```bash
python3 scripts/validate_plugin.py
python3 -m unittest discover -s tests
codex plugin add futu-personal@futu-personal-local
python3 scripts/inspect_mcp.py
```

Codex 使用安装后的缓存副本。安装器如果未刷新，先 `codex plugin remove futu-personal@futu-personal-local`，再重新安装。随后新建聊天加载新版本。

## 可选订单草稿

`futu-personal-order-draft` 和 `scripts/order_draft.py` 保留为本地附加功能，用于生成用户明确指定参数的股票限价单草稿。脚本使用 Python Decimal 处理金额，没有网络或订单提交能力。

草稿功能只覆盖它声明支持的参数，不表示富途全量订单类型或市场范围，也不替代插件接入的真实交易和模拟交易接口。

## 验证记录

验收分别记录本地插件加载、MCP 工具发现、OAuth 实际授予范围和具体接口调用。任何一项成功都不能代替其余项目。

### 0.2.0 当前验收

- 源码配置已声明四类 scopes，并移除工具白名单和黑名单。
- 安装缓存已刷新为 0.2.0，Codex 原生客户端实际发现 101 个工具；实盘四工具、自选修改、模拟历史订单、加密货币接口和新增期权组合接口均已注册。
- `scripts/inspect_mcp.py` 可重复核对当前工具集合，不读取凭据、不调用写工具、不保存新聊天。
- 原有 OAuth 已保存，四类权限实际授予范围等待重新授权后在富途页面核对。
- 本轮只验证完整注册及读接口，不发送真实订单、自选写请求或模拟订单。
- 四类权限及真实交易调用尚未写成已通过；未执行的操作保留为未验证。

### 0.1.0 历史验收（2026-10-12）

以下记录属于旧版只读配置，不代表 `0.2.0` 的当前工具集合或写权限：

- 本地安装、OAuth 保存和富途 MCP 工具发现通过。
- Codex 加载 82 个工具，与当时的静态允许列表一致；实盘执行及自选修改工具未加载。
- 使用 Codex 原生 MCP 客户端调用 `quote_market_snapshot`，参数为 `{"code_list":["HK.00700"]}`，返回 `ret_code=0`、`ret_msg=success`。
- 腾讯快照返回 `last_price=424.8`、`data_date=2026-10-09`、`update_time=1791533277000`。这是接口数据时间，不能当作 2026-10-12 的盘中价格。
- 当时未验收账户查询或模拟操作。只读调用使用临时运行上下文，没有启动模型回合或保存新聊天。

## 移除

```bash
codex plugin remove futu-personal@futu-personal-local
codex plugin marketplace remove futu-personal-local
```

卸载本地插件不等于撤销富途 OAuth 授权；授权由富途账户侧管理。
