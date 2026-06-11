"""
GEO MCP Server — 内容评分工具
对网页内容进行 GEO 评分（0-100），评估被 AI 引擎引用的潜力
"""
from __future__ import annotations

from typing import Any, Optional

from ..utils import fetch_url, score_geo, cache_get, cache_set


def score_content(url: str, target_keywords: Optional[list[str]] = None) -> dict[str, Any]:
    """
    对指定 URL 的内容进行 GEO 评分。

    从五个维度评估内容被 AI 引擎引用的潜力：
    1. Entity Clarity (25pts) — 实体定义清晰度
    2. Citation Worthiness (25pts) — 可引用性
    3. Content Structure (20pts) — 内容结构
    4. Freshness Signals (15pts) — 时效性
    5. Authority Signals (15pts) — 权威性

    Args:
        url: 要分析的网页 URL
        target_keywords: 可选，目标关键词列表，用于相关性评估

    Returns:
        详细的 GEO 评分报告，包含总分、各维度得分和改进建议
    """
    cache_key = f"score:{url}"
    cached = cache_get(cache_key)
    if cached:
        return {**cached, "_cached": True}

    content = fetch_url(url)
    if not content["success"]:
        return {
            "url": url,
            "success": False,
            "error": content["error"],
            "total": 0,
            "grade": "N/A — 无法抓取页面",
        }

    scores = score_geo(content)

    result = {
        "url": url,
        "success": True,
        "title": content["title"],
        "meta_description": content["meta_description"],
        "word_count": content["word_count"],
        **scores,
    }

    # 关键词相关性评估
    if target_keywords:
        full_text = " ".join(content["paragraphs"]).lower()
        title_lower = content["title"].lower()
        keyword_matches = {}
        for kw in target_keywords:
            kw_lower = kw.lower()
            count = full_text.count(kw_lower)
            in_title = kw_lower in title_lower
            keyword_matches[kw] = {
                "count": count,
                "in_title": in_title,
                "density": round(count / max(content["word_count"], 1) * 100, 2),
            }
        result["keyword_analysis"] = keyword_matches

    cache_set(cache_key, result)
    return result
