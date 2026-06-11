"""
GEO MCP Server — 品牌监控工具
追踪品牌在 AI 生态中的引用变化趋势
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from ..utils import search_citations


MONITOR_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "monitor_data")


def _ensure_monitor_dir():
    os.makedirs(MONITOR_DIR, exist_ok=True)


def _get_monitor_file(brand: str) -> str:
    safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in brand)
    return os.path.join(MONITOR_DIR, f"{safe_name}.json")


def track_brand(brand: str) -> dict[str, Any]:
    """
    记录品牌当前的 AI 引用状态，用于后续趋势对比。

    每次调用会保存一个快照，与历史数据对比生成趋势报告。

    Args:
        brand: 品牌名称

    Returns:
        当前状态 + 趋势变化
    """
    _ensure_monitor_dir()

    current = search_citations(brand)
    current["recorded_at"] = datetime.now().isoformat()

    filepath = _get_monitor_file(brand)
    history = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = {}

    # 保存快照
    snapshots = history.get("snapshots", [])
    snapshots.append({
        "timestamp": current["recorded_at"],
        "overall_score": current["overall_presence_score"],
        "engines": {
            ek: {
                "mentioned": ed["mentioned"],
                "mentions": ed["mention_count_estimate"],
                "sentiment": ed["sentiment"],
            }
            for ek, ed in current["engines"].items()
        },
    })
    # 只保留最近50个快照
    if len(snapshots) > 50:
        snapshots = snapshots[-50:]

    history["brand"] = brand
    history["snapshots"] = snapshots
    history["last_updated"] = current["recorded_at"]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    # 计算趋势
    trend = _calculate_trend(snapshots)

    return {
        "brand": brand,
        "current_score": current["overall_presence_score"],
        "snapshots_count": len(snapshots),
        "trend": trend,
        "current_detail": current,
        "history_file": filepath,
    }


def get_trend(brand: str) -> dict[str, Any]:
    """
    获取品牌的历史引用趋势。

    Args:
        brand: 品牌名称

    Returns:
        历史趋势数据（需先调用 track_brand 积累数据）
    """
    filepath = _get_monitor_file(brand)
    if not os.path.exists(filepath):
        return {
            "brand": brand,
            "error": "没有历史数据，请先调用 geo_brand_monitor 开始追踪",
            "snapshots_count": 0,
        }

    with open(filepath, "r", encoding="utf-8") as f:
        history = json.load(f)

    snapshots = history.get("snapshots", [])
    trend = _calculate_trend(snapshots)

    return {
        "brand": brand,
        "first_recorded": snapshots[0]["timestamp"] if snapshots else None,
        "last_recorded": snapshots[-1]["timestamp"] if snapshots else None,
        "snapshots_count": len(snapshots),
        "trend": trend,
        "snapshots": snapshots,
    }


def _calculate_trend(snapshots: list[dict]) -> dict[str, Any]:
    """计算趋势"""
    if len(snapshots) < 2:
        return {
            "direction": "insufficient_data",
            "description": "需要至少2个数据点才能分析趋势",
            "change": 0,
        }

    first = snapshots[0]["overall_score"]
    last = snapshots[-1]["overall_score"]
    change = last - first

    if change > 10:
        direction = "📈 显著上升"
    elif change > 2:
        direction = "↗️ 小幅上升"
    elif change > -2:
        direction = "➡️ 基本持平"
    elif change > -10:
        direction = "↘️ 小幅下降"
    else:
        direction = "📉 显著下降"

    # 变化率
    rate = round(change / max(first, 1) * 100, 1) if first > 0 else 0

    # 引擎级别趋势
    engine_trends = {}
    if snapshots:
        first_engines = snapshots[0].get("engines", {})
        last_engines = snapshots[-1].get("engines", {})
        for ek in first_engines:
            first_mentions = first_engines[ek].get("mentions", 0)
            last_mentions = last_engines.get(ek, {}).get("mentions", 0)
            engine_trends[ek] = {
                "first": first_mentions,
                "last": last_mentions,
                "change": last_mentions - first_mentions,
            }

    return {
        "direction": direction,
        "description": f"{direction}（{'+' if change > 0 else ''}{change}分, {'+' if rate > 0 else ''}{rate}%）",
        "change": change,
        "change_rate_percent": rate,
        "engine_trends": engine_trends,
        "data_points": len(snapshots),
    }
