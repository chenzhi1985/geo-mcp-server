"""
GEO MCP Server — License Key 系统
=================================
HMAC-SHA256 签名密钥，支持 Free / Pro / Team 三级

生成: python payment/license.py --generate --tier pro --user someone
验证: python payment/license.py --verify <key>
"""
from __future__ import annotations

import os
import json
import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Any


# ── 配置 ──────────────────────────────────────────────────────
LICENSE_SECRET = os.environ.get("GEO_LICENSE_SECRET", "geo-mcp-change-me-in-production")
LICENSE_FILE = os.path.join(os.path.dirname(__file__), "..", "licenses.json")

# 三级定价
TIERS = {
    "free": {
        "name": "Free",
        "daily_queries": 50,
        "tools": ["geo_check_citation", "geo_content_score"],
        "resources": ["geo://best-practices", "geo://checklist"],
        "search_engines": 2,
        "competitor_limit": 3,
        "price_cny": 0,
        "price_usd": 0,
    },
    "pro": {
        "name": "Pro",
        "daily_queries": 10000,
        "tools": ["geo_check_citation", "geo_content_score", "geo_competitor_gap",
                   "geo_brand_monitor", "geo_brand_trend", "geo_ai_visibility"],
        "resources": ["geo://best-practices", "geo://checklist"],
        "search_engines": 4,
        "competitor_limit": 10,
        "price_cny": 149,
        "price_usd": 19,
    },
    "team": {
        "name": "Team",
        "daily_queries": 999999,
        "tools": ["geo_check_citation", "geo_content_score", "geo_competitor_gap",
                   "geo_brand_monitor", "geo_brand_trend", "geo_ai_visibility"],
        "resources": ["geo://best-practices", "geo://checklist"],
        "search_engines": 4,
        "competitor_limit": 50,
        "price_cny": 399,
        "price_usd": 49,
    },
    "enterprise": {
        "name": "Enterprise",
        "daily_queries": 99999999,
        "tools": ["geo_check_citation", "geo_content_score", "geo_competitor_gap",
                   "geo_brand_monitor", "geo_brand_trend", "geo_ai_visibility"],
        "resources": ["geo://best-practices", "geo://checklist"],
        "search_engines": 4,
        "competitor_limit": 999,
        "price_cny": "定制",
        "price_usd": "Custom",
    },
}


# ── 密钥生成 ──────────────────────────────────────────────────

def generate_key(tier: str, user_id: str, valid_days: int = 365) -> str:
    """生成 License Key"""
    if tier not in TIERS:
        raise ValueError(f"Invalid tier: {tier}. Choose from {list(TIERS.keys())}")
    prefix = "GEO"
    nonce = secrets.token_hex(4)
    payload = f"{tier}|{user_id}|{nonce}|{valid_days}"
    signature = hmac.new(
        LICENSE_SECRET.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()[:16]
    key = f"{prefix}-{tier.upper()}-{signature}-{nonce}"
    return key


def verify_key(key: str) -> Optional[dict[str, Any]]:
    """验证 License Key，返回 tier 信息或 None"""
    try:
        parts = key.split("-")
        if len(parts) != 4 or parts[0] != "GEO":
            return None
        tier = parts[1].lower()
        signature = parts[2]
        nonce = parts[3]
        if tier not in TIERS:
            return None
        # 从已存的 licenses 中查找
        licenses = _load_licenses()
        if key in licenses:
            lic = licenses[key]
            if lic.get("expires_at"):
                expires = datetime.fromisoformat(lic["expires_at"])
                if datetime.now() > expires:
                    return None  # 已过期
            return {
                "tier": tier,
                "user_id": lic.get("user_id", "unknown"),
                "expires_at": lic.get("expires_at"),
                **TIERS[tier],
            }
        return None
    except Exception:
        return None


# ── 许可证存储 ────────────────────────────────────────────────

def _load_licenses() -> dict:
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_licenses(data: dict) -> None:
    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def register_key(key: str, tier: str, user_id: str, valid_days: int = 365) -> dict:
    """注册一个 License Key"""
    expires = (datetime.now() + timedelta(days=valid_days)).isoformat()
    licenses = _load_licenses()
    licenses[key] = {
        "tier": tier,
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "expires_at": expires,
    }
    _save_licenses(licenses)
    return {"key": key, "tier": tier, "user_id": user_id, "expires_at": expires}


# ── 速率限制 ──────────────────────────────────────────────────

_usage: dict[str, dict[str, int]] = {}  # {date: {user_id: count}}


def check_quota(user_id: str, tier_info: dict) -> dict[str, Any]:
    """检查用户今日剩余配额"""
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in _usage:
        _usage.clear()
        _usage[today] = {}
    used = _usage[today].get(user_id, 0)
    limit = tier_info.get("daily_queries", 50)
    remaining = max(0, limit - used)
    return {
        "used_today": used,
        "limit": limit,
        "remaining": remaining,
        "allowed": remaining > 0,
    }


def record_usage(user_id: str) -> None:
    """记录一次 API 调用"""
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in _usage:
        _usage[today] = {}
    _usage[today][user_id] = _usage[today].get(user_id, 0) + 1


# ── CLI ───────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if "--generate" in sys.argv:
        tier = "pro"
        user = "test"
        days = 365
        for i, arg in enumerate(sys.argv):
            if arg == "--tier" and i + 1 < len(sys.argv):
                tier = sys.argv[i + 1]
            if arg == "--user" and i + 1 < len(sys.argv):
                user = sys.argv[i + 1]
            if arg == "--days" and i + 1 < len(sys.argv):
                days = int(sys.argv[i + 1])
        key = generate_key(tier, user, days)
        print(f"License Key: {key}")
        # 自动注册
        result = register_key(key, tier, user, days)
        print(f"Tier: {result['tier']}")
        print(f"Expires: {result['expires_at']}")
    elif "--verify" in sys.argv:
        for arg in sys.argv:
            if arg.startswith("GEO-"):
                info = verify_key(arg)
                if info:
                    print(f"✅ Valid — Tier: {info['tier']}, User: {info['user_id']}")
                else:
                    print("❌ Invalid or expired")
    else:
        print("Usage:")
        print("  python license.py --generate --tier pro --user someone")
        print("  python license.py --verify GEO-PRO-xxxx-xxxx")
