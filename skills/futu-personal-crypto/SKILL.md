---
name: futu-personal-crypto
description: 富途数字资产账户与完整 MCP 接口，包括余额、购买力、订单、成交查询，以及下单、改单和撤单接口。
---

# 富途数字资产账户与交易接口

使用当前插件加载的 `crypto_account_*` MCP 工具，按工具名后缀识别，不硬编码宿主前缀。本 Skill 提供数字资产接口路由与参数核对，不提供交易策略。加载 Skill 或检查工具能力不代表已调用服务，也不授权任何写请求。

先读取插件根目录 `preferences.json`，如有 `preferences.local.json`，只覆盖其中明确提供的偏好。不要读取或存储登录凭据。
账户 ID 取自当前授权账户列表的 `acc_id`，确认用户选择的账户支持数字资产。不能从股票账户名称或账户短号推断 ID；切换账户时重新确认。

## 意图路由与必填参数

下表来自 MCP 工具 schema；每次使用仍以当前加载的 schema 和字段说明为准。工具新增或字段变化时不要沿用旧参数。

| 用户想要 | 工具 | schema 的 required 参数 |
|---|---|---|
| 总资产、现金及数字资产余额 | `crypto_account_total_balance` | `acc_id` |
| 购买力、最大可交易数量 | `crypto_account_purchasing_power` | `acc_id` |
| 活跃订单 | `crypto_account_active_orders` | `acc_id` |
| 历史订单 | `crypto_account_order_history` | `acc_id`、`start_time`、`end_time`、`page_size` |
| 指定订单详情 | `crypto_account_order_detail` | `acc_id`、`orderId` |
| 指定订单的成交 | `crypto_account_fills` | `acc_id`、`order_id` |
| 历史成交 | `crypto_account_fills_history` | `acc_id`、`start_time`、`end_time`、`page_size` |
| 下单接口 | `crypto_account_create_order` | `acc_id`、`req_id`、`side`、`symbol`、`ord_type`、`time_in_force` |
| 改单接口 | `crypto_account_modify_order` | `acc_id`、`orderId`、`req_id`、`price`、`qty`、`order_version`、`conditional_info` |
| 撤单接口 | `crypto_account_cancel_order` | `acc_id`、`orderId`、`req_id` |

## 参数核对

- 数字资产使用交易对，如 `BTCUSD`，不能套用股票的 `市场.代码` 格式。交易对、方向、订单类型与数量由用户明确指定，不猜账户或枚举。
- 订单详情、改单和撤单参数名为 `orderId`；成交查询为 `order_id`，不能混用。
- 历史订单和历史成交的 `start_time` / `end_time` 为 Unix 微秒整数，查询区间须在过去三个月内；历史订单的时间不能为 `0`。`page_size` 为字符串，并在这两个历史接口中列为必填。
- 分页使用 `page_flag`，第一页省略，后续沿用响应游标。活跃订单和历史订单每页最多 50 条；总分页遵循个人配置的 `max_pages` / `max_rows`，截断时说明。
- 订单详情可用逗号分隔多个订单 ID，最多 20 单。
- 购买力接口的 required 列表只有 `acc_id`，但指定限价类型时字段说明要求 `price > 0`；仍需核对交易资产 `coin`、结算币种 `currency` 与 `order_type`，不能把 required 列表当作全部业务条件。
- 下单的 `qty` 与 `cash_order_qty` 互斥，按金额下单不支持 `SELL`；限价类型需 `price`。相关字段未全部列入 required，必须结合当前字段说明核对。金额和数量均为字符串，不按股票整数股数处理。
- 下单使用 `ord_type`，购买力使用 `order_type`。当前字段说明列出 `LIMIT`、`MARKET`、止盈和止损类型；有效期使用 `TIF_GTC` 或 `TIF_IOC`，适用关系按当前 schema 核对，不能套用股票的 `DAY` / `GTC`。
- 改单当前只支持止盈和止损订单。`order_version` 使用最新订单详情的版本号；`conditional_info` 必须包含 `trigger_price`。`TAKE_PROFIT_MARKET` / `STOP_LOSS_MARKET` 的改单 `price` 按 schema 传 `0`，不自行转换其他订单参数。
- 三个写接口都要求 `req_id`，字段说明建议 `{timestamp}_{uuid}`，长度 16–64。它是幂等标识；同一请求不得因超时而换一个标识重新提交。

## 写操作与结果核对

每次写操作先展示数字资产账户、操作类型、交易对、方向、数量或金额、订单类型、价格、触发价、有效期及目标订单 ID。改单展示原订单与拟修改参数；撤单说明目标订单和当前状态。收到针对该具体操作的明确确认后，仍按当前宿主规则判断是否可调用接口。参数变化后重新确认，批量操作逐笔核对。

返回成功不等于成交。使用 `crypto_account_order_detail`、活跃/历史订单或成交工具核对结果；写请求超时或结果不明确时先查状态，不自动重复提交。无法确认结果时说明未核对的部分。

余额和成交结果注明资产、币种及数据时间，保留数值精度，不将不同资产或币种直接相加。当前工具 schema 没有声明 OAuth scope 映射，不能凭 `crypto_account_` 前缀推断权限；权限以富途授权和接口实际返回为准。

宿主安全规则不因接口注册或用户确认而改变；实际操作仍受当前平台规则约束。
