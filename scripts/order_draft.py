#!/usr/bin/env python3
"""Render a stock limit-order draft. No network or broker execution."""

import argparse
import json
import re
from decimal import Decimal, InvalidOperation, localcontext


def positive_decimal(value: str) -> Decimal:
    if len(value) > 64 or not re.fullmatch(r"(?:\d+(?:\.\d*)?|\.\d+)", value):
        raise ValueError("数量和价格必须是普通十进制正数，不接受指数或特殊值")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("无效的十进制数") from exc
    if not number.is_finite() or number <= 0:
        raise ValueError("数量和价格必须大于零")
    return number


def build_draft(account_id, symbol, side, quantity, limit_price, currency, time_in_force="DAY"):
    if not account_id.strip() or any(ord(c) < 32 for c in account_id):
        raise ValueError("必须提供有效的账户 ID")
    if not re.fullmatch(r"(?:HK|US|SH|SZ|SG|JP|CA|AU|MY|KR)\.[A-Z0-9][A-Z0-9.-]*", symbol):
        raise ValueError("股票代码必须包含市场前缀，例如 HK.00700 或 US.AAPL")
    if side not in {"BUY", "SELL"} or time_in_force not in {"DAY", "GTC"}:
        raise ValueError("首版只支持 BUY/SELL 与 DAY/GTC")
    if not re.fullmatch(r"[A-Z]{3}", currency):
        raise ValueError("币种必须为三位大写代码")
    qty = positive_decimal(quantity)
    price = positive_decimal(limit_price)
    if qty != qty.to_integral_value():
        raise ValueError("首版股票草稿只支持整数股数")
    with localcontext() as context:
        context.prec = 160
        amount = format(qty * price, "f")
    return {
        "status": "DRAFT_ONLY",
        "execution": "manual_in_futu_client",
        "environment": "REAL",
        "account_id": account_id.strip(),
        "symbol": symbol,
        "side": side,
        "quantity": str(int(qty)),
        "quantity_unit": "shares",
        "order_type": "LIMIT",
        "limit_price": format(price, "f"),
        "currency": currency,
        "time_in_force": time_in_force,
        "estimated_notional_excluding_fees": amount,
        "submitted": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ["account-id", "symbol", "side", "quantity", "limit-price", "currency"]:
        parser.add_argument("--" + field, required=True)
    parser.add_argument("--time-in-force", choices=["DAY", "GTC"], default="DAY")
    args = vars(parser.parse_args())
    try:
        draft = build_draft(**args)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(draft, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
