"""
GEO MCP Server — 订单管理
=========================
存储用户购买记录，支持"待确认 → 已支付 → Key 已签发"状态流转

订单文件: orders.json
"""
import os
import json
from datetime import datetime
from typing import Optional

ORDERS_FILE = os.environ.get("GEO_ORDERS_FILE", "/var/lib/geo-mcp/orders.json")


def _load() -> list[dict]:
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save(orders: list[dict]) -> None:
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)


def create_order(tier: str, email: str, payment_method: str = "wechat", tx_hash: str = "") -> dict:
    """创建新订单"""
    orders = _load()
    order_id = f"GEO-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(orders)+1:04d}"
    order = {
        "order_id": order_id,
        "tier": tier,
        "email": email,
        "payment_method": payment_method,
        "tx_hash": tx_hash,
        "amount_cny": {"pro": 149, "team": 399, "enterprise": 0}.get(tier, 0),
        "amount_usd": {"pro": 19, "team": 49, "enterprise": 0}.get(tier, 0),
        "status": "pending",       # pending → paid → key_issued
        "license_key": "",
        "created_at": datetime.now().isoformat(),
        "paid_at": "",
        "key_issued_at": "",
    }
    orders.append(order)
    _save(orders)
    return order


def mark_paid(order_id: str) -> Optional[dict]:
    """标记已支付"""
    orders = _load()
    for o in orders:
        if o["order_id"] == order_id:
            o["status"] = "paid"
            o["paid_at"] = datetime.now().isoformat()
            _save(orders)
            return o
    return None


def issue_key(order_id: str, license_key: str) -> Optional[dict]:
    """签发 License Key"""
    orders = _load()
    for o in orders:
        if o["order_id"] == order_id:
            o["status"] = "key_issued"
            o["license_key"] = license_key
            o["key_issued_at"] = datetime.now().isoformat()
            _save(orders)
            return o
    return None


def get_pending() -> list[dict]:
    """获取待确认的订单"""
    return [o for o in _load() if o["status"] == "pending"]


def get_paid_awaiting_key() -> list[dict]:
    """获取已支付但未签发 Key 的订单"""
    return [o for o in _load() if o["status"] == "paid"]


def get_all() -> list[dict]:
    return _load()


def get_stats() -> dict:
    orders = _load()
    pending = sum(1 for o in orders if o["status"] == "pending")
    paid = sum(1 for o in orders if o["status"] == "paid")
    issued = sum(1 for o in orders if o["status"] == "key_issued")
    revenue_cny = sum(
        o.get("amount_cny", 0) for o in orders
        if o["status"] in ("paid", "key_issued")
    )
    return {
        "total_orders": len(orders),
        "pending": pending,
        "paid_awaiting_key": paid,
        "key_issued": issued,
        "revenue_cny": revenue_cny,
    }
