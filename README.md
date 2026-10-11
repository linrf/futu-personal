# Futu Personal

你自己的 Codex 富途插件：行情、选股、资讯、账户查询、逐笔确认的模拟交易，以及供你在富途客户端手动提交的实盘订单草稿。

基于 [FutunnOpen/futu-agent-plugin](https://github.com/FutunnOpen/futu-agent-plugin)，上游基线为 `a1cfd82087453e0089a11fedc45f36ea85039930`（2026-09-10）。保留 MIT License。本项目不是富途官方插件。

## 安装和首次使用

需要本机 `codex` CLI。插件连接富途托管的 MCP，不需要安装 OpenD。

```bash
codex plugin marketplace add /Users/bytedance/github/futu-personal
codex plugin add futu-personal@futu-personal-local
codex mcp login futu-personal --scopes quote:read,trade:read
```

首次试用只申请行情和交易查询权限。富途授权页会展示当前客户端和账户实际可授予的范围；有些权限可能不可选。登录、协议接受和最终授权由用户在页面完成，不要把账号密码粘贴到聊天。
安装后新建 Codex 聊天，选择 `@Futu Personal`。
首次试用先查询一只股票的报价，核对币种、时间和行情权限。账户查询时明确选择真实或模拟账户。模拟写操作逐笔展示摘要并等待确认。
当前只读授权不代表模拟写操作已获得权限；模拟交易需要另行核对富途要求的授权范围。

不要将插件已安装、授权成功或请求返回成功当作行情/订单验收已通过。

## 个人设置

`preferences.json` 是可提交的默认配置。账户默认为空、常用市场默认为空，不猜测你的账户或偏好。
可用 `preferences.local.json` 覆盖个人偏好，该文件已被 Git 忽略。只保存偏好，不保存密码或 OAuth Token。
修改源码或配置后运行：

```bash
python3 scripts/validate_plugin.py
codex plugin add futu-personal@futu-personal-local
```

Codex 使用安装后的缓存副本；安装器如果未刷新，先 `codex plugin remove futu-personal@futu-personal-local`，再重新安装。随后新建聊天加载新版本。

## 与上游的差异

- 只提供 Codex 插件，去掉其他平台入口和符号链接。
- 行情、筛选、资讯参考文档沿用上游；分页有上限，报价要求注明数据时间、币种和时段。
- 同一会话中已明确选择的账户可继续查询，切换账户或环境时重新确认。
- `.mcp.json` 使用工具允许列表，真实交易工具不加载；自选股写操作也未启用。
- 保留逐笔模拟交易确认，结果不明确时先查订单，不能自动重试写操作。
- 订单草稿使用 Python Decimal 保留价格精度，脚本没有网络或订单提交能力。

## 本地检查

```bash
python3 scripts/validate_plugin.py
python3 -m unittest discover -s tests
```

检查覆盖 manifest/marketplace 路径、Skills、参考链接、工具允许列表，以及订单草稿的精度和输入限制。
OAuth、富途工具实际返回的名称/权限和只读查询需要另外验收；这个仓库没有富途 MCP 服务端实现。

## OAuth 客户端差异

本地插件复用富途 MCP，OAuth 由 Codex 客户端发起。修改本地插件的名称和 Skills 不会把它变成 WorkBuddy 的 OAuth 客户端。
WorkBuddy 授权应用页面中的“交易执行”说明该客户端已获得对应权限，不能作为 Codex 也已获得同一权限的证据。最终以各自授权页和实际工具返回为准。

## 移除

```bash
codex plugin remove futu-personal@futu-personal-local
codex plugin marketplace remove futu-personal-local
```

卸载本地插件不等于撤销富途 OAuth 授权；授权由富途账户侧管理。
