"""
GEO MCP Server — 竞品分析工具
对比多个品牌在 AI 引擎中的引用存在，发现差距和机会
"""
from __future__ import annotations

from typing import Any

from ..utils import search_citations, cache_get, cache_set


def competitor_gap(
    brand: str,
    competitors: list[str],
    topic: str = "",
) -> dict[str, Any]:
    """
    对比你的品牌与竞品在 AI 引擎中的引用差距。

    对每个品牌执行 AI 引用检测，并生成对比矩阵。

    Args:
        brand: 你的品牌名称
        competitors: 竞品品牌名称列表（最多10个）
        topic: 可选，聚焦特定话题/行业

    Returns:
        竞品对比矩阵、差距分析和机会点
    """
    cache_key = f"competitor:{brand}:{','.join(sorted(competitors))}:{topic}"
    cached = cache_get(cache_key)
    if cached:
        return {**cached, "_cached": True}

    all_brands = [brand] + competitors[:10]
    results = {}
    for b in all_brands:
        results[b] = search_citations(b, topic if topic else None)

    # 构建对比矩阵
    matrix = []
    for b, r in results.items():
        engines_detail = {}
        for ek, ed in r["engines"].items():
            engines_detail[ek] = {
                "mentioned": ed["mentioned"],
                "mentions": ed["mention_count_estimate"],
                "sentiment": ed["sentiment"],
            }
        matrix.append({
            "brand": b,
            "overall_score": r["overall_presence_score"],
            "engines": engines_detail,
            "summary": r["summary"],
        })

    # 排序
    matrix.sort(key=lambda x: x["overall_score"], reverse=True)

    # 排名
    my_rank = next((i + 1 for i, m in enumerate(matrix) if m["brand"] == brand), len(matrix))

    # 差距分析
    top = matrix[0]
    gaps = []
    if my_rank > 1:
        if top["overall_score"] > 0:
            gap_percent = round(
                (top["overall_score"] - results[brand]["overall_presence_score"])
                / top["overall_score"] * 100, 1
            )
        else:
            gap_percent = 0
        # 找出具体差距
        for ek in ["chatgpt", "claude", "gemini", "perplexity"]:
            my_mentions = results[brand]["engines"].get(ek, {}).get("mention_count_estimate", 0)
            top_mentions = results[top["brand"]]["engines"].get(ek, {}).get("mention_count_estimate", 0)
            if top_mentions > my_mentions:
                gaps.append({
                    "engine": ek,
                    "leader": top["brand"],
                    "leader_mentions": top_mentions,
                    "your_mentions": my_mentions,
                    "delta": top_mentions - my_mentions,
                })

    # 机会点
    opportunities = []
    # 找出竞争最少的引擎
    engine_competition = {}
    for ek in ["chatgpt", "claude", "gemini", "perplexity"]:
        mentioned_count = sum(
            1 for m in matrix
            if m["engines"].get(ek, {}).get("mentioned", False)
        )
        engine_competition[ek] = mentioned_count
    least_competitive = min(engine_competition, key=engine_competition.get)
    opportunities.append({
        "type": "low_competition_engine",
        "engine": least_competitive,
        "description": f"竞品在 {least_competitive} 上存在较少，是建立先发优势的机会",
    })

    # 引文空白
    competitor_keywords = set()
    for b, r in results.items():
        for e in r["engines"].values():
            for ctx in e.get("context", []):
                words = ctx.lower().split()
                competitor_keywords.update(
                    w for w in words if len(w) > 5 and w not in ["which", "their", "about", "these"]
                )

    result = {
        "brand": brand,
        "topic": topic,
        "my_rank": f"#{my_rank}/{len(all_brands)}",
        "my_score": results[brand]["overall_presence_score"],
        "matrix": matrix,
        "gaps": gaps,
        "opportunities": opportunities,
        "insights": [
            f"📊 在 {len(all_brands)} 个品牌中排名第 {my_rank}",
            f"📈 最高引用分: {top['brand']} ({top['overall_score']})",
            f"🎯 最大机会: 抢占 {least_competitive} 生态",
        ] if gaps else [
            f"🏆 你在 {len(all_brands)} 个品牌中排名第一!",
            "保持内容更新频率，防止竞品追赶",
            f"探索更深度的 {least_competitive} 集成",
        ],
    }

    cache_set(cache_key, result)
    return result
