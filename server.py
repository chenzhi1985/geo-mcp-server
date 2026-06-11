#!/usr/bin/env python3
"""
GEO MCP Server — Generative Engine Optimization
================================================
检测品牌在 AI 引擎中的引用存在、评分内容 GEO 优化程度、
分析竞品差距、追踪引用趋势。

用于 Claude Code / Cursor / 任何 MCP 兼容客户端。

启动方式:
    python server.py
    或
    mcp dev server.py    (MCP Inspector 调试模式)

上架后用户配置 Claude Desktop:
    {
      "mcpServers": {
        "geo-optimizer": {
          "command": "python",
          "args": ["d:/项目管理/MCP Server/geo-mcp-server/server.py"]
        }
      }
    }
"""

from mcp.server.fastmcp import FastMCP

from src.tools.citation import check_citation, analyze_ai_visibility
from src.tools.scorer import score_content
from src.tools.competitor import competitor_gap
from src.tools.monitor import track_brand, get_trend

# ── Server 初始化 ─────────────────────────────────────────────

mcp = FastMCP(name="GEO Optimizer")

# ── 工具定义 ──────────────────────────────────────────────────


@mcp.tool()
def geo_check_citation(
    brand: str,
    topic: str = "",
    engines: str = "",
) -> dict:
    """
    检测品牌在 AI 引擎（ChatGPT/Claude/Gemini/Perplexity）中的引用存在情况。

    通过搜索 AI 平台文档、社区讨论和技术内容，判断品牌是否被 AI 生态引用。
    返回各引擎的提及数量、情感倾向和整体引用指数。

    使用场景：
    - "我的品牌在 ChatGPT 的回答中出现过吗？"
    - "Claude 会推荐我的产品吗？"
    - "对比我在不同 AI 平台上的可见度"

    Args:
        brand: 品牌名称，例如 "Apple", "特斯拉", "Notion"
        topic: 可选，聚焦特定话题，例如 "AI tools", "电动汽车"
        engines: 可选，逗号分隔的引擎列表，例如 "chatgpt,claude"。留空检测全部。
    """
    engine_list = [e.strip() for e in engines.split(",") if e.strip()] if engines else None
    return check_citation(
        brand=brand,
        topic=topic if topic else None,
        engines=engine_list,
    )


@mcp.tool()
def geo_content_score(
    url: str,
    keywords: str = "",
) -> dict:
    """
    对网页内容进行 GEO 评分（0-100分），评估被 AI 引擎引用的潜力。

    从五个维度评估：
    ┌─────────────────────────┬──────┬──────────────────────────┐
    │ 维度                     │ 满分  │ 评估内容                   │
    ├─────────────────────────┼──────┼──────────────────────────┤
    │ Entity Clarity           │  25  │ Schema.org、实体定义、Meta  │
    │ Citation Worthiness      │  25  │ 统计数据、引用、独特见解     │
    │ Content Structure        │  20  │ 标题层级、列表、FAQ         │
    │ Freshness Signals        │  15  │ 日期、更新频率              │
    │ Authority Signals        │  15  │ 外部链接、作者、HTTPS       │
    └─────────────────────────┴──────┴──────────────────────────┘

    使用场景：
    - "我的这篇博客文章有多大可能被AI引用？"
    - "如何优化着陆页让ChatGPT推荐我的产品？"

    Args:
        url: 要分析的网页 URL
        keywords: 可选，逗号分隔的目标关键词
    """
    kw_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else None
    return score_content(url=url, target_keywords=kw_list)


@mcp.tool()
def geo_competitor_gap(
    brand: str,
    competitors: str,
    topic: str = "",
) -> dict:
    """
    对比你的品牌与竞品在 AI 引擎中的引用差距。

    对每个品牌执行全引擎引用检测，生成对比矩阵，并提供：
    - 排名位置
    - 具体差距（哪个引擎、差多少）
    - 低竞争机会点
    - 可执行的追赶建议

    使用场景：
    - "Notion 和 Confluence 在 AI 引用上谁更强？"
    - "我们在 AI 可见度上比竞品差在哪里？"

    Args:
        brand: 你的品牌名称
        competitors: 竞品名称，逗号分隔，例如 "Notion,Confluence,Evernote"
        topic: 可选，聚焦特定话题
    """
    competitor_list = [c.strip() for c in competitors.split(",") if c.strip()]
    return competitor_gap(
        brand=brand,
        competitors=competitor_list,
        topic=topic,
    )


@mcp.tool()
def geo_brand_monitor(brand: str) -> dict:
    """
    追踪品牌在 AI 生态中的引用变化趋势。

    每次调用会保存当前快照，与历史数据对比，生成趋势报告。
    定期调用此工具（如每周一次）可建立完整的引用变化历史。

    使用场景：
    - "我的 GEO 优化效果如何？"
    - "品牌 AI 引用这个月有没有增长？"

    Args:
        brand: 品牌名称
    """
    return track_brand(brand=brand)


@mcp.tool()
def geo_brand_trend(brand: str) -> dict:
    """
    查看品牌的历史引用趋势（需要先通过 geo_brand_monitor 积累数据）。

    Args:
        brand: 品牌名称
    """
    return get_trend(brand=brand)


@mcp.tool()
def geo_ai_visibility(
    brand: str,
    urls: str,
) -> dict:
    """
    综合分析品牌的 AI 可见度 — 结合引用检测 + 内容GEO评分。

    这是最全面的分析工具，帮助你了解品牌在 AI 时代的整体可见度。

    使用场景：
    - "全面诊断我的品牌在AI搜索中的表现"
    - "给投资人展示我们的AI可见度报告"

    Args:
        brand: 品牌名称
        urls: 品牌关键页面 URL，逗号分隔，例如 "https://example.com,https://example.com/blog"
    """
    url_list = [u.strip() for u in urls.split(",") if u.strip()]
    return analyze_ai_visibility(brand=brand, content_urls=url_list)


# ── 资源定义 ──────────────────────────────────────────────────


@mcp.resource("geo://best-practices")
def geo_best_practices() -> str:
    """GEO 最佳实践指南（2026版）"""
    return """# 🔥 GEO (Generative Engine Optimization) 最佳实践 2026

## 核心理念
GEO 的目标不是欺骗 AI，而是让内容对 AI 更易理解、更值得引用。

## 1. 实体清晰化 (Entity Clarity)
- ✅ 在首段明确定义核心实体（品牌/产品/人物）
- ✅ 使用 Schema.org 结构化数据（Organization, Article, FAQPage, Product）
- ✅ Meta Description 控制在 120-160 字符
- ✅ 使用一致的品牌名称和专有名词

## 2. 可引用性 (Citation Worthiness)
- ✅ 内容中加入具体数据（百分比、金额、数量）
- ✅ 引用权威来源并标注出处
- ✅ 提供独特的观点、分析框架或原创研究
- ✅ 使用「根据XX研究」「数据显示」「调查发现」等句式
- ✅ 创建统计数据、对比表格、时间线

## 3. 内容结构 (Content Structure)
- ✅ 有且仅有一个 H1 标题
- ✅ 使用 H2/H3 建立清晰的文档结构
- ✅ 使用有序/无序列表组织信息
- ✅ 添加 FAQ 结构化数据
- ✅ 长文内容目标 1500+ 词
- ✅ 每个段落聚焦一个观点

## 4. 时效性 (Freshness)
- ✅ 标注发布日期和最近更新日期
- ✅ 标题或首段加入年份
- ✅ 每季度更新关键内容
- ✅ 建立内容更新日历

## 5. 权威性 (Authority)
- ✅ 引用并链接到权威外部来源
- ✅ 添加作者简介和资质说明
- ✅ 所有图片包含描述性 ALT 文本
- ✅ 确保网站使用 HTTPS
- ✅ 获取来自高权威域名的 backlink

## 6. AI 平台特殊优化
- ChatGPT: 偏好结构化、定义清晰、数据丰富的内容
- Claude: 偏好长篇、分析深入、有引用的内容
- Gemini: 偏好与 Google 生态集成、Schema 完善的内容
- Perplexity: 偏好时效性强、来源可验证的内容

## 7. 监测与迭代
- 每月检测品牌 AI 引用变化
- 追踪竞品在 AI 生态中的动向
- A/B 测试内容结构对 AI 引用的影响
"""


@mcp.resource("geo://checklist")
def geo_checklist() -> str:
    """GEO 优化检查清单"""
    return """# ✅ GEO 优化检查清单

## 基础优化 (每一项都必须完成)
- [ ] 网站使用 HTTPS
- [ ] 每个页面有唯一的 Meta Description (120-160字符)
- [ ] 有且仅有一个 H1
- [ ] 使用 H2/H3 建立层级结构
- [ ] 添加 Schema.org 结构化数据
- [ ] 图片有 ALT 文本

## 内容优化
- [ ] 首段包含核心实体定义
- [ ] 内容包含具体数据/统计
- [ ] 引用权威来源并链接
- [ ] 使用列表组织信息
- [ ] 字数 1500+ (深度内容)
- [ ] 标注发布/更新日期

## 进阶优化
- [ ] 添加 FAQ 结构化数据
- [ ] 作者页面包含资质信息
- [ ] 建立内部链接网络
- [ ] 定期更新旧内容
- [ ] 发布原创研究/数据
- [ ] 在权威平台建立引用

## 持续监测
- [ ] 每月检查品牌 AI 引用
- [ ] 追踪竞品 AI 引用变化
- [ ] 分析高引用内容特征
- [ ] A/B 测试优化策略
"""


# ── 提示词定义 ─────────────────────────────────────────────────


@mcp.prompt()
def geo_optimize() -> str:
    """获取 GEO 内容优化提示词"""
    return """你是一位 GEO（生成式引擎优化）专家。请根据以下框架帮我优化内容，使其更容易被 AI 引擎引用：

## 分析框架
1. **实体清晰度**：核心实体是否在前100词内明确定义？是否使用了 Schema.org 结构化数据？
2. **可引用性**：内容是否包含可被 AI 摘录的数据、统计、定义、步骤？
3. **结构优化**：标题层级是否清晰？是否使用了列表？是否有 FAQ？
4. **时效性**：是否有明确的发布日期？内容是否反映了最新信息？
5. **权威性**：是否引用了可靠来源？作者信息是否完整？

## 输出格式
- 当前内容 GEO 评分（0-100）
- 逐维度分析
- 具体的修改建议（给出修改后的文本）
- 优先级排序（P0/P1/P2）

请开始分析我提供的内容。"""


@mcp.prompt()
def geo_strategy() -> str:
    """获取 GEO 策略规划提示词"""
    return """你是一位 GEO（生成式引擎优化）策略顾问。帮我制定品牌在 AI 引擎生态中的可见度提升策略。

## 策略框架
1. **现状诊断**：品牌目前在 AI 引擎中的引用情况如何？
2. **内容差距分析**：对比竞品，我们的内容在哪些维度落后？
3. **内容规划**：应该创建哪些类型的内容来提升AI引用？
4. **分发策略**：内容应该发布在哪些平台？
5. **监测计划**：如何追踪效果？

## 关键问题
- 当前 AI 引用最弱的是哪个平台（ChatGPT/Claude/Gemini/Perplexity）？
- 竞品在哪些内容类型上有优势？
- 品牌的独特数据和见解是什么？如何转化为可引用内容？
- 3个月、6个月、12个月的阶段性目标是什么？

请给出可执行的 90 天 GEO 提升计划。"""


# ── 入口 ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    # 支持 stdio 模式（Claude Desktop）和 SSE 模式（调试）
    transport = "stdio"
    if "--sse" in sys.argv:
        transport = "sse"
    elif "--dev" in sys.argv:
        # MCP Inspector 模式
        print("🔍 启动 GEO MCP Server (dev mode)...")
        print("   在另一个终端运行: npx @modelcontextprotocol/inspector")
    mcp.run(transport=transport)
