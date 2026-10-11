---
name: futu-personal-account
description: 查询富途真实或模拟账户的资金、持仓、订单和成交，以及逐笔确认的模拟交易。
---

# 个人富途账户与模拟交易

使用当前插件已加载的 MCP 工具，按工具名后缀识别，不硬编码平台前缀。
先读取插件根目录 `preferences.json`；如有 `preferences.local.json`，只覆盖其中明确提供的偏好，不读取或存储登录凭据。

## 账户查询

首次账户查询时调用 `account_authorized_trd_accs` 与 `sim_trade_account_list`，展示账户类型及脱敏 ID，让用户选择。
会话中已明确选择、仍在当前授权列表内的账户可继续使用；切换真实/模拟环境或账户时重新确认。
配置中的 `query_account_id` 只作为待验证的查询偏好，不授权任何写操作。

| 查询 | 真实账户 | 模拟账户 |
|---|---|---|
| 资金 | `account_funds` | `sim_trade_cash_info` |
| 持仓 | `account_positions` | `sim_trade_position_list` |
| 订单 | `account_orders_active` / `account_orders_history` / `account_orders_detail` | 使用已加载的模拟订单查询工具 |
| 成交 | `account_order_fills_today` / `account_fills_history` | 使用已加载的模拟成交查询工具 |
| 最大可买卖 | `account_trading_info` | `sim_trade_max_buy_sell` |

标注账户类型、币种、数据时间及盈亏口径，不混合币种求和。
ID 不完整或接口字段缺失时说明缺失，不从账户名称推断 ID。
分页遵循个人配置的 `max_pages` / `max_rows`，默认最多 3 页、100 条；说明截断，按需继续。
价格保留接口精度；盈亏比例先确认分母和币种。

## 模拟交易

只使用 `sim_trade_input_order`、`sim_trade_modify_order`、`sim_trade_cancel_order`。
每笔操作先展示模拟账户、标的、方向、数量及单位、订单类型、价格、有效期（接口支持时），等待用户明确确认。
修改任何订单参数后重新确认。确认仅针对展示的那笔操作，不沿用到其他订单。
返回订单 ID 后查询实际订单状态；接口成功不等于成交。如没有已加载的模拟订单查询工具，明确说明订单状态尚未核对。
写请求超时或结果不明确时先查询订单，不自动重复提交；无法核对时停下并说明。

## 实盘订单草稿

真实下单、改单、撤单与风控确认不在本插件可用工具列表中。
需要实盘操作时，使用同包的 `futu-personal-order-draft` 生成草稿，由用户在富途客户端手动执行。
不得调用其他插件或直接 HTTP/SDK 来替代本插件缺失的实盘执行工具。

## 参数参考

- 真实账户查询：[trading-real.md](reference/trading-real.md)
- 模拟账户与操作：[trading-sim.md](reference/trading-sim.md)
