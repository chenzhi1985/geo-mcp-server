#!/usr/bin/env python3
"""
GEO MCP Server — License 管理后台
=================================
签发 / 查询 / 吊销 License Key

用法:
    python payment/admin.py list                     # 列出所有 Key
    python payment/admin.py issue pro user@email.com # 签发新 Key
    python payment/admin.py revoke <key>             # 吊销 Key
    python payment/admin.py stats                    # 统计概览
"""
import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from payment.license import (
    generate_key, register_key, verify_key, TIERS,
    LICENSE_FILE, _load_licenses, _save_licenses,
)


def cmd_list():
    """列出所有 License"""
    licenses = _load_licenses()
    if not licenses:
        print("📭 暂无 License Key")
        return

    print(f"{'Tier':12s} {'User':25s} {'Expires':20s} {'Key'}")
    print("-" * 90)
    for key, info in sorted(licenses.items(), key=lambda x: x[1].get("expires_at", "")):
        tier = info.get("tier", "?")
        user = info.get("user_id", "?")[:24]
        expires = info.get("expires_at", "?")[:19]
        key_short = key[:30] + "..."
        expired = "🔴" if expires < datetime.now().isoformat() else "🟢"
        print(f"{expired} {tier:10s} {user:25s} {expires:20s} {key_short}")


def cmd_issue():
    """签发新 Key"""
    if len(sys.argv) < 4:
        print("用法: python payment/admin.py issue <tier> <email> [days]")
        print(f"Tiers: {', '.join(TIERS.keys())}")
        return

    tier = sys.argv[2]
    user_id = sys.argv[3]
    days = int(sys.argv[4]) if len(sys.argv) > 4 else 365

    if tier not in TIERS or tier == "free":
        print(f"❌ Invalid tier: {tier}")
        return

    key = generate_key(tier, user_id, days)
    result = register_key(key, tier, user_id, days)

    print("✅ License Key 已签发")
    print(f"   Key:      {key}")
    print(f"   Tier:     {result['tier'].upper()}")
    print(f"   User:     {user_id}")
    print(f"   Expires:  {result['expires_at']}")
    print(f"   Price:    ¥{TIERS[tier]['price_cny']} / ${TIERS[tier]['price_usd']}")
    print()
    print("📋 发给用户:")
    print(f"   感谢购买 GEO MCP Server {tier.upper()}！")
    print(f"   你的 License Key: {key}")
    print(f"   设置方法: export GEO_LICENSE_KEY={key}")
    print(f"   到期时间: {result['expires_at']}")


def cmd_revoke():
    """吊销 Key"""
    if len(sys.argv) < 3:
        print("用法: python payment/admin.py revoke <key>")
        return

    key = sys.argv[2]
    licenses = _load_licenses()
    if key in licenses:
        info = licenses.pop(key)
        _save_licenses(licenses)
        print(f"🗑️  已吊销: {info.get('user_id')} ({info.get('tier')})")
    else:
        print("❌ Key 不存在")


def cmd_stats():
    """统计概览"""
    licenses = _load_licenses()
    now = datetime.now()
    active = 0
    expired = 0
    by_tier = {}
    revenue_cny = 0

    for key, info in licenses.items():
        tier = info.get("tier", "free")
        by_tier[tier] = by_tier.get(tier, 0) + 1
        expires = info.get("expires_at", "")
        if expires and datetime.fromisoformat(expires) > now:
            active += 1
            price = TIERS.get(tier, {}).get("price_cny", 0)
            if isinstance(price, (int, float)):
                revenue_cny += price
        else:
            expired += 1

    print("📊 GEO MCP Server — 销售概览")
    print(f"   License 总数:  {len(licenses)}")
    print(f"   活跃:          {active}")
    print(f"   过期:          {expired}")
    print(f"   预估收入:      ¥{revenue_cny:,}")
    print()
    for tier, count in sorted(by_tier.items()):
        price = TIERS.get(tier, {}).get("price_cny", 0)
        print(f"   {tier:12s}: {count} 个 × ¥{price} = ¥{count * (price if isinstance(price, (int, float)) else 0):,}")


def cmd_verify():
    """验证 Key"""
    if len(sys.argv) < 3:
        print("用法: python payment/admin.py verify <key>")
        return

    key = sys.argv[2]
    info = verify_key(key)
    if info:
        print(f"✅ 有效 — {info['tier'].upper()} / {info['user_id']}")
    else:
        print("❌ 无效或已过期")


# ── CLI ───────────────────────────────────────────────────────
COMMANDS = {
    "list": cmd_list,
    "issue": cmd_issue,
    "revoke": cmd_revoke,
    "stats": cmd_stats,
    "verify": cmd_verify,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("GEO MCP Server — License 管理后台")
        print()
        for name, fn in COMMANDS.items():
            print(f"  {name:10s} — {fn.__doc__}")
        sys.exit(1)

    COMMANDS[sys.argv[1]]()
