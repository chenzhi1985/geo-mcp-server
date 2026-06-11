"""
GEO MCP Server — 引用检测工具
检测品牌在 AI 引擎（ChatGPT/Claude/Gemini/Perplexity）中的引用存在
"""
from __future__ import annotations

from typing import Optional, Any

from ..utils import search_citations, cache_get, cache_set, AI_ENGINES


def check_citation(
    brand: str,
    topic: Optional[str] = None,
    engines: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    检测品牌在 AI 引擎中的引用存在情况。

    通过多维度搜索判断品牌是否被 AI 生态讨论和引用：
    1. 在 AI 平台官方社区/文档中被提及的频率
    2. 在技术社区（Reddit/HN/GitHub）中与 AI 工具关联讨论
    3. 品牌内容的 GEO 优化程度

    Args:
        brand: 品牌名称
        topic: 可选，聚焦特定话题
        engines: 可选，指定引擎列表（chatgpt, claude, gemini, perplexity）

    Returns:
        包含各引擎引用详情、整体引用指数和优化建议
    """
    cache_key = f"citation:{brand}:{topic}:{engines}"
    cached = cache_get(cache_key)
    if cached:
        return {**cached, "_cached": True}

    if engines:
        # 过滤仅需要的引擎
        for key in list(AI_ENGINES.keys()):
            if key not in engines:
                del AI_ENGINES[key]

    result = search_citations(brand, topic)

    # 添加优化建议
    if result["overall_presence_score"] < 30:
        result["recommendations"] = [
            "在品牌官网添加结构化数据（Schema.org Organization/Article）",
            f"创建围绕 {brand} 的深度内容（白皮书、行业报告、原创研究）",
            "在 AI 开发者社区（GitHub/HuggingFace）建立存在",
            "优化品牌内容使其更容易被 AI 摘要和引用（使用清晰的实体定义、统计数据、列表结构）",
            f"在 Reddit r/artificial、Hacker News 等社区分享 {brand} 相关的 AI 用例",
        ]
    elif result["overall_presence_score"] < 70:
        result["recommendations"] = [
            "增加原创数据和行业洞察的发布频率",
            "与 AI 领域的 KOL 合作增加品牌提及",
            "将品牌内容发布到 AI 训练数据源（Wikipedia、权威媒体、学术论文）",
        ]
    else:
        result["recommendations"] = [
            "维护现有内容并定期更新以保持时效性",
            "监控竞品引用变化，保持领先地位",
            "探索 AI Agent 生态中的品牌集成机会（MCP Server、Plugin）",
        ]

    cache_set(cache_key, result)
    return result


def analyze_ai_visibility(brand: str, content_urls: list[str]) -> dict[str, Any]:
    """
    综合分析品牌的 AI 可见度。

    结合引用检测和内容GEO评分，给出整体可见度评估。

    Args:
        brand: 品牌名称
        content_urls: 品牌的关键内容 URL 列表

    Returns:
        综合 AI 可见度报告
    """
    from .scorer import score_content

    citation = search_citations(brand)
    content_scores = []
    for url in content_urls[:5]:
        try:
            score = score_content(url)
            content_scores.append(score)
        except Exception:
            pass

    avg_content_score = (
        sum(s["total"] for s in content_scores) / len(content_scores)
        if content_scores else 0
    )

    return {
        "brand": brand,
        "citation_score": citation["overall_presence_score"],
        "avg_content_geo_score": round(avg_content_score, 1),
        "composite_score": round(
            citation["overall_presence_score"] * 0.4 + avg_content_score * 0.6, 1
        ),
        "citation_detail": citation,
        "content_analysis": content_scores,
        "verdict": _get_verdict(citation["overall_presence_score"], avg_content_score),
    }


def _get_verdict(citation_score: float, content_score: float) -> str:
    composite = citation_score * 0.4 + content_score * 0.6
    if composite >= 75:
        return "🏆 该品牌在AI生态中有很强的存在感，AI模型有较高概率引用其内容"
    elif composite >= 50:
        return "📈 该品牌有一定的AI可见度，通过针对性优化可以显著提升"
    elif composite >= 30:
        return "🔧 该品牌AI可见度偏低，建议从内容GEO优化和社区建设两端同时发力"
    else:
        return "🚀 该品牌AI可见度很低，需要从零开始建设GEO策略"
