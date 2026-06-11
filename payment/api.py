"""
GEO MCP Server — 支付 API
==========================
FastAPI 后端，处理微信支付回调 + x402 验证 + License Key 签发

启动: uvicorn payment.api:app --port 8899
部署: 挂到 reedsail.com/geo-pro/ 后面
"""
from __future__ import annotations

import os
import json
import hashlib
import time
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from .license import generate_key, register_key, verify_key, TIERS
from .x402 import create_payment_request, verify_payment, process_payment

app = FastAPI(title="GEO MCP Payment API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 挂载静态文件（微信支付页面）
WECHAT_DIR = os.path.join(os.path.dirname(__file__), "wechat")
if os.path.exists(WECHAT_DIR):
    app.mount("/buy", StaticFiles(directory=WECHAT_DIR, html=True), name="buy")


# ── 数据模型 ──────────────────────────────────────────────────

class PurchaseRequest(BaseModel):
    tier: str
    email: str = ""
    payment_method: str = "wechat"  # wechat | x402
    payment_id: str = ""


class LicenseResponse(BaseModel):
    success: bool
    license_key: str = ""
    tier: str = ""
    expires_at: str = ""
    message: str = ""


# ── 微信支付回调 ──────────────────────────────────────────────

# 存储支付中的订单
_pending_orders: dict[str, dict] = {}


@app.post("/api/pay/wechat/create")
async def create_wechat_order(req: PurchaseRequest):
    """创建微信支付订单"""
    if req.tier not in TIERS or req.tier == "free":
        raise HTTPException(400, f"Invalid tier: {req.tier}")

    price = TIERS[req.tier]["price_cny"]
    if isinstance(price, str):
        raise HTTPException(400, "Enterprise tier requires custom pricing")

    order_id = f"GEO-{req.tier.upper()}-{int(time.time())}"
    _pending_orders[order_id] = {
        "tier": req.tier,
        "email": req.email,
        "price_cny": price,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    return {
        "order_id": order_id,
        "tier": req.tier,
        "price_cny": price,
        "status": "pending",
        # 实际部署: 返回微信支付预支付订单参数
        "wechat_params": {
            "appId": os.environ.get("WECHAT_APP_ID", ""),
            "timeStamp": str(int(time.time())),
            "nonceStr": hashlib.md5(str(time.time()).encode()).hexdigest()[:16],
            "package": f"prepay_id={order_id}",
            "signType": "MD5",
        },
    }


@app.post("/api/pay/wechat/callback")
async def wechat_callback(order_id: str = Query(...)):
    """微信支付成功回调 → 自动签发 License Key"""
    order = _pending_orders.get(order_id)
    if not order:
        raise HTTPException(404, "Order not found")

    order["status"] = "paid"
    tier = order["tier"]
    user_id = order.get("email", order_id)

    # 生成 License Key
    key = generate_key(tier, user_id)
    result = register_key(key, tier, user_id)

    return LicenseResponse(
        success=True,
        license_key=key,
        tier=result["tier"],
        expires_at=result["expires_at"],
        message=f"License key generated. Valid until {result['expires_at']}",
    )


# ── x402 支付 ─────────────────────────────────────────────────

@app.post("/api/pay/x402/create")
async def create_x402_request(req: PurchaseRequest):
    """创建 x402 支付请求"""
    result = create_payment_request(req.tier, req.email or "anonymous")
    return result


@app.post("/api/pay/x402/verify")
async def verify_x402_payment(payment_id: str):
    """验证 x402 支付并签发 License"""
    # 查找订单信息
    # 实际部署: 从数据库查
    tier = "pro"
    user_id = "anonymous"
    result = process_payment(payment_id, tier, user_id)
    return result


# ── License 查询 ──────────────────────────────────────────────

@app.get("/api/license/verify")
async def api_verify_key(key: str = Query(...)):
    """验证 License Key 是否有效"""
    info = verify_key(key)
    if info:
        return {"valid": True, "tier": info["tier"], "user_id": info["user_id"],
                "expires_at": info.get("expires_at"), "daily_queries": info.get("daily_queries")}
    return {"valid": False, "message": "Invalid or expired license key"}


@app.get("/api/license/tiers")
async def list_tiers():
    """列出所有定价方案"""
    return {
        "tiers": {
            k: {"name": v["name"], "price_cny": v.get("price_cny"), "price_usd": v.get("price_usd"),
                "daily_queries": v.get("daily_queries")}
            for k, v in TIERS.items()
        }
    }


# ── 启动 ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print("💰 GEO MCP Payment API")
    print("   微信支付页面: http://localhost:8899/buy/")
    print("   API 文档:     http://localhost:8899/docs")
    uvicorn.run(app, host="0.0.0.0", port=8899)
