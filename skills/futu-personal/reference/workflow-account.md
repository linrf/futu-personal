
# 富途账户与交易接口

使用当前插件已加载的 MCP 工具，按工具名后缀识别，不硬编码平台前缀。工具参数以当前服务端 schema 为准；参考文档用于解释业务含义。没有匹配路由时先检查实际工具列表，不因本地参考缺失而判为不支持。
先读取插件根目录 `preferences.json`；如有 `preferences.local.json`，只覆盖明确提供的偏好，不读取或存储登录凭据。

## 账户与环境

首次账户操作时查询 `account_authorized_trd_accs` 和 `sim_trade_account_list`，展示真实/模拟类型及脱敏 ID，让用户选择。
同一会话已明确选择且仍在授权列表内的账户可继续使用；切换账户或真实/模拟环境时重新核对。
`query_account_id` 是待验证偏好，不代表写操作授权。不得根据名称、旧响应或真实账户 ID 猜测模拟账户参数。

## 工具路由

| 操作 | 真实账户 | 模拟账户 |
|---|---|---|
| 资金 | `account_funds` | `sim_trade_cash_info` |
| 持仓 | `account_positions` | `sim_trade_position_list` |
| 活跃/历史订单 | `account_orders_active` / `account_orders_history` | `sim_trade_history_order_list` 或当前提供的模拟订单查询工具 |
| 订单详情 | `account_orders_detail` | 按当前模拟查询 schema 选择 |
| 成交 | `account_order_fills_today` / `account_fills_history` | 按当前模拟查询 schema 选择 |
| 最大可买卖 | `account_trading_info` | `sim_trade_max_buy_sell` |
| 下单 | `trading_order_place` | `sim_trade_input_order` |
| 改单 | `trading_order_replace` | `sim_trade_modify_order` |
| 撤单 | `trading_order_cancel` | `sim_trade_cancel_order` |
| 风控确认 | `trading_order_confirm` | 以实际返回和 schema 为准 |

## 参数与操作状态

接口注册、OAuth 授权和实际操作许可分别判断，遵守当前宿主执行规则。完整接口注册不授权 Agent 代做受限的金融活动。
写操作摘要包含账户及环境、标的、方向、数量及单位、订单类型、价格、有效期、交易时段和修改前后差异。按用户给定参数整理，不自行决定标的、数量或价格。
每次写操作需要针对该摘要的明确确认；参数改变后重新确认，不能将一次确认复用于其他订单。

支持的订单方向、类型、交易所、时段、多腿结构以 `trading_order_place` 的当前 schema 为准，不限制为股票 LIMIT 单。港股行情代码 `HK` 与交易所 `SEHK` 是不同字段，不能机械替换。
价格保留用户及接口精度，不统一四舍五入至两位小数。市价单、A 股改单及多腿订单的限制见实盘参考，并按当前 schema 复核。
若响应 `need_order_confirm=true`，订单尚未生效；展示当前风控原因，核对该次响应的 `confirm_id`，不得复用旧确认 ID。
返回订单 ID 后核对订单状态；接口成功不代表成交。超时或结果不明确时先查订单，不自动重复写请求；没有可核对的查询工具时说明状态未确认。

## 查询输出

标注环境、币种、数据时间和盈亏口径，不混合币种求和。分页遵循 `max_pages` / `max_rows`，默认最多 3 页、100 条，说明截断并按需继续。
权限不足时展示缺少的权限和授权入口，不使用其他客户端凭据或直接 HTTP/SDK 绕过授权。

## 参数参考

- 真实账户查询：[trading-real.md](./trading-real.md)
- 真实下单、改单、撤单、确认：[trading-real-order.md](./trading-real-order.md)
- 模拟接口：[trading-sim.md](./trading-sim.md)。历史订单等未收入旧文档的工具读取当前 schema，不猜测字段。
- 需要离线整理股票 LIMIT 单参数时，可选用同包 [订单草稿工作流](./workflow-order-draft.md)；该脚本不是完整交易接口的替代。
