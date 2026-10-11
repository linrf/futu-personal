---
name: futu-personal
description: 富途全量 MCP 总路由。用于行情、K线、自选、股票与衍生品筛选、资讯与研究、真实及模拟账户、证券交易、数字资产和可选订单草稿；按需求读取业务参考并使用当前工具 schema。
---

# 富途总路由

这是本插件唯一的 Skill 入口。先识别需求，再选择工具和按需读取参考文档；不一次加载全部参考。
插件连接富途官方 MCP，保留服务端发布的全部工具。下面的工具名是路由示例，不是允许列表。

## 选择工具与参考

1. 获取当前插件已加载的工具名称、描述和参数 schema。按实际工具名后缀识别工具，不硬编码宿主前缀。
2. 根据下表找到业务类别，读取对应 workflow；需要参数或返回字段细节时，再读取该 workflow 引用的参数文档。
3. 核对当前 schema 中的必填参数、枚举、精度、分页和权限。当前 schema 优先于旧参考，不猜测未声明的字段。
4. 若需求没有直接匹配下表，先检查完整工具列表及描述，再选择新工具；本地参考未列出不表示服务端不支持。

| 需求 | 常用工具后缀 | 按需读取 |
|---|---|---|
| 行情、K线、盘口、分时、逐笔、市场状态、板块、自选查询或修改、组合报价 | `quote_stock_quote`、`quote_market_snapshot`、`quote_modify_user_security`、`quote_combo_option_quote` | [行情与自选](reference/workflow-quote.md) |
| 股票、窝轮、期权筛选，期权组合、价差、期货、IPO | `quote_stock_screen`、`quote_option_strategy`、`quote_option_strategy_spread` | [筛选与衍生品](reference/workflow-screen.md) |
| 新闻、社区、经济日历、财报、估值、评级、股东、公司行为、资金流、卖空与经纪商 | `quote_news_search`、`quote_financials_statements`、`quote_capital_flow` | [资讯与研究](reference/workflow-news.md) |
| 真实及模拟账户、资金、持仓、订单、成交、最大可买卖；证券下单、改单、撤单、风控确认 | `account_authorized_trd_accs`、`sim_trade_account_list`、`trading_order_place`、`trading_order_replace`、`trading_order_cancel`、`trading_order_confirm` | [账户与证券交易](reference/workflow-account.md) |
| 数字资产余额、购买力、订单、成交、下单、改单、撤单 | `crypto_account_total_balance`、`crypto_account_create_order`、`crypto_account_modify_order`、`crypto_account_cancel_order` | [数字资产](reference/workflow-crypto.md) |
| 用户明确选择离线整理股票限价单参数 | 本地 `scripts/order_draft.py` | [可选订单草稿](reference/workflow-order-draft.md) |

跨类别需求只读取相关 workflow。期权链、波动率和期货资料见下方参数索引，不因没有专门的 Skill 而遗漏。
订单草稿是附加能力，不能将所有交易需求自动改为草稿；完整真实交易与模拟交易工具继续保留。

## 共用规则

- 先读取插件根目录 [preferences.json](../../preferences.json)。如存在 `preferences.local.json`，只覆盖明确提供的偏好，不读取登录凭据。账户或市场为空时不猜测。
- 区分行情代码与交易所字段，例如行情 `HK.00700` 与真实订单 `SEHK.00700`；按具体工具核对，不机械替换。先确认市场、代码、名称、数量单位和交易时段。
- 行情、K线和持仓注明市场、币种、数据时间及交易时段；K线注明复权方式。保留接口精度，盈亏说明口径，不混合币种求和。
- 优先使用 `limit` / `num` 控制查询量。分页遵循个人配置，默认最多 3 页、100 条；达到上限时说明截断，按需继续，不无限遍历。
- 首次账户操作查询真实与模拟账户列表，展示类型和脱敏 ID 供用户选择。同一会话已明确选择且仍在授权列表内的账户可复用；切换账户或环境时重新核对。数字资产使用对应的账户流程。
- 交易及其他写操作先展示具体对象和参数，并取得针对本次操作的明确确认。参数改变后重新确认；不自行决定标的、方向、数量或价格。
- 工具注册、OAuth 授权和实际操作成功分别判断。宿主的安全规则仍适用，完整接口注册不授权 Agent 代做受限金融活动。
- 返回成功或订单 ID 不等于成交。查询实际状态；写请求超时或结果不明确时先核对，不自动重发。风控确认使用当前响应的 `confirm_id`，先展示提示，不复用旧 ID。
- 权限不足时说明接口错误与缺少的权限。OAuth 登录及授权在富途页面完成，不读取、输出或转移 Token，不使用其他客户端凭据或直接 HTTP/SDK 绕过授权。

## 参数文档索引

只读取当前问题需要的文件。六份 workflow 保留原业务规则，下面十六份参数文档保留上游原文；其中尚未记载的新工具仍按当前 schema 使用。

| 参数类别 | 文档 |
|---|---|
| 报价、快照、K线 | [quote-realtime.md](reference/quote-realtime.md) |
| 盘口、逐笔、分时、市场状态、交易日历 | [quote-tick.md](reference/quote-tick.md) |
| 自选 | [quote-watchlist.md](reference/quote-watchlist.md) |
| 股票筛选与板块 | [quote-screening.md](reference/quote-screening.md) |
| 期权链、波动率、筛选 | [quote-options.md](reference/quote-options.md) |
| 期货、窝轮与牛熊证 | [quote-futures-warrants.md](reference/quote-futures-warrants.md) |
| 新闻、社区、经济日历、IPO | [quote-news.md](reference/quote-news.md) |
| 财报、营收、业绩日 | [quote-financials.md](reference/quote-financials.md) |
| 估值、评级、晨星、公司信息 | [quote-research.md](reference/quote-research.md) |
| 股东与内部人 | [quote-shareholders.md](reference/quote-shareholders.md) |
| 分红、回购、拆合股与复权 | [quote-corporate-actions.md](reference/quote-corporate-actions.md) |
| 资金流向 | [quote-capital.md](reference/quote-capital.md) |
| 卖空、经纪商、股票基本信息 | [quote-short-broker.md](reference/quote-short-broker.md) |
| 真实账户、资金、持仓、订单、成交与交易容量 | [trading-real.md](reference/trading-real.md) |
| 真实下单、改单、撤单与风控确认 | [trading-real-order.md](reference/trading-real-order.md) |
| 模拟交易 | [trading-sim.md](reference/trading-sim.md) |
