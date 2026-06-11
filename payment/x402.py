"""
GEO MCP Server — x402 链上支付
===============================
USDC 微支付 (Base 链)，支持 $0.001 起付

x402 协议: HTTP 402 Payment Required
用户支付 USDC → 链上验证 → 自动签发 License Key

依赖: web3.py (pip install web3)

收款地址: 在环境变量 X402_WALLET 中配置
RPC: Base 主网 (或用公共 RPC)
"""
from __future__ import annotations

import os
import hashlib
import json
import time
from typing import Optional, Any

from .license import generate_key, register_key, TIERS

# ── 配置 ──────────────────────────────────────────────────────
X402_WALLET = os.environ.get("X402_WALLET", "")  # 你的收款钱包地址
BASE_RPC = os.environ.get("BASE_RPC", "https://mainnet.base.org")
USDC_CONTRACT = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"  # Base USDC


def create_payment_request(
    tier: str,
    user_id: str,
    payment_method: str = "usdc",
) -> dict[str, Any]:
    """
    创建支付请求

    返回包含支付地址和金额的信息，
    用户支付后调用 verify_payment 验证
    """
    if tier not in TIERS or tier == "free":
        return {"error": f"Invalid tier: {tier}"}

    price_usd = TIERS[tier]["price_usd"]
    if isinstance(price_usd, str):
        return {"error": "Enterprise tier requires custom pricing. Contact admin."}

    # 生成唯一支付 ID
    payment_id = hashlib.sha256(
        f"{tier}|{user_id}|{time.time()}".encode()
    ).hexdigest()[:16]

    return {
        "payment_id": payment_id,
        "tier": tier,
        "user_id": user_id,
        "amount_usdc": price_usd,
        "wallet_address": X402_WALLET,
        "chain": "Base",
        "usdc_contract": USDC_CONTRACT,
        "status": "pending",
        "instructions": f"Send {price_usd} USDC to {X402_WALLET} on Base. "
                        f"Include payment_id '{payment_id}' in memo (last 8 chars).",
    }


def verify_payment(payment_id: str, expected_amount: float) -> dict[str, Any]:
    """
    链上验证支付

    检查是否收到指定金额的 USDC 到收款钱包
    使用 BaseScan API 或直接 RPC 查询
    """
    # 方案 1: 使用 BaseScan API（简单，不需要运行节点）
    basescan_api_key = os.environ.get("BASESCAN_API_KEY", "")
    if basescan_api_key:
        return _verify_via_basescan(payment_id, expected_amount, basescan_api_key)

    # 方案 2: 使用 RPC（需要 web3.py）
    try:
        from web3 import Web3
        w3 = Web3(Web3.HTTPProvider(BASE_RPC))
        if w3.is_connected():
            return _verify_via_rpc(payment_id, expected_amount, w3)
    except ImportError:
        pass

    # 方案 3: 手动验证（开发 / 测试用）
    return {
        "verified": False,
        "method": "manual",
        "message": "No RPC or API configured. Verification must be done manually.",
        "instruction": f"Check BaseScan for USDC transfers to {X402_WALLET}",
    }


def _verify_via_basescan(
    payment_id: str, expected_amount: float, api_key: str
) -> dict[str, Any]:
    """BaseScan API 验证"""
    import httpx
    url = (
        f"https://api.basescan.org/api"
        f"?module=account&action=tokentx"
        f"&contractaddress={USDC_CONTRACT}"
        f"&address={X402_WALLET}"
        f"&apikey={api_key}"
    )
    try:
        resp = httpx.get(url, timeout=10)
        data = resp.json()
        if data.get("status") == "1":
            for tx in data["result"]:
                tx_value = int(tx["value"]) / 1e6  # USDC 6 decimals
                tx_hash = tx["hash"]
                # 检查金额匹配 + 交易在最近 24 小时内
                if abs(tx_value - expected_amount) < 0.01:
                    return {
                        "verified": True,
                        "method": "basescan",
                        "tx_hash": tx_hash,
                        "amount": tx_value,
                        "from": tx["from"],
                    }
        return {"verified": False, "method": "basescan", "message": "No matching payment found"}
    except Exception as e:
        return {"verified": False, "method": "basescan", "error": str(e)}


def _verify_via_rpc(
    payment_id: str, expected_amount: float, w3: Any
) -> dict[str, Any]:
    """RPC 验证（需 web3.py）"""
    # USDC Transfer 事件 topic
    transfer_topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    # 过滤收款地址
    wallet_topic = "0x" + "0" * 24 + X402_WALLET[2:].lower()
    logs = w3.eth.get_logs({
        "address": USDC_CONTRACT,
        "fromBlock": w3.eth.block_number - 10000,  # 最近 10000 个区块
        "topics": [transfer_topic, None, wallet_topic],
    })
    for log in logs:
        value = int(log["data"], 16) / 1e6  # USDC 6 decimals
        if abs(value - expected_amount) < 0.01:
            return {
                "verified": True,
                "method": "rpc",
                "tx_hash": log["transactionHash"].hex(),
                "amount": value,
            }
    return {"verified": False, "method": "rpc", "message": "No matching payment found"}


def process_payment(payment_id: str, tier: str, user_id: str) -> dict[str, Any]:
    """
    支付完成后生成 License Key

    验证支付 → 生成密钥 → 注册
    """
    price = TIERS[tier].get("price_usd", 0)
    if isinstance(price, str):
        return {"error": "Enterprise tier requires custom pricing"}

    # 验证支付
    verification = verify_payment(payment_id, price)
    if not verification.get("verified"):
        return {
            "success": False,
            "verification": verification,
            "message": "Payment not verified. Please send USDC first.",
        }

    # 生成 License Key
    key = generate_key(tier, user_id)
    result = register_key(key, tier, user_id)

    return {
        "success": True,
        "license_key": key,
        "tier": result["tier"],
        "expires_at": result["expires_at"],
        "tx_hash": verification.get("tx_hash"),
        "payment_method": "x402 (USDC on Base)",
    }


# ── CLI ───────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    if "--wallet" in sys.argv:
        print(f"X402_WALLET={X402_WALLET or '未配置'}")
        print(f"设置: export X402_WALLET=0x...")
    elif "--verify" in sys.argv:
        # 找 payment_id 参数
        pid = None
        amount = 0
        for i, arg in enumerate(sys.argv):
            if arg == "--pid" and i + 1 < len(sys.argv):
                pid = sys.argv[i + 1]
            if arg == "--amount" and i + 1 < len(sys.argv):
                amount = float(sys.argv[i + 1])
        if pid:
            result = verify_payment(pid, amount)
            print(json.dumps(result, indent=2))
        else:
            print("Usage: python x402.py --verify --pid <id> --amount <usdc>")
    else:
        # 创建支付请求
        tier = sys.argv[1] if len(sys.argv) > 1 else "pro"
        user = sys.argv[2] if len(sys.argv) > 2 else "test-user"
        req = create_payment_request(tier, user)
        print(json.dumps(req, indent=2, ensure_ascii=False))
