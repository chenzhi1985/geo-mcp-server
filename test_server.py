"""
GEO MCP Server — 单元测试 & 集成测试
=====================================
运行方式:
    python test_server.py              # 全部测试
    python test_server.py --quick      # 快速冒烟（跳过网络）
    python test_server.py --verbose    # 详细输出
"""
import sys
import json
import time
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils import fetch_url, score_geo, search_citations, cache_get, cache_set
from src.tools.citation import check_citation, analyze_ai_visibility
from src.tools.scorer import score_content
from src.tools.competitor import competitor_gap
from src.tools.monitor import track_brand, get_trend

PASS = 0
FAIL = 0


def test(name: str):
    """装饰器：测试包装器"""
    def decorator(fn):
        def wrapper():
            global PASS, FAIL
            try:
                fn()
                PASS += 1
                print(f"  ✅ {name}")
            except AssertionError as e:
                FAIL += 1
                print(f"  ❌ {name} — {e}")
            except Exception as e:
                FAIL += 1
                print(f"  💥 {name} — {type(e).__name__}: {e}")
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════
# 层级 A: 单元测试 — 评分引擎
# ═══════════════════════════════════════════════════════════════


@test("评分引擎：空内容返回低分")
def test_empty_content_scores_low():
    empty = {
        "url": "https://test.com",
        "success": True, "title": "", "meta_description": "",
        "headings": [], "paragraphs": [], "lists": [],
        "word_count": 0, "structured_data": [], "entities": [],
        "links_internal": [], "links_external": [], "images": [],
        "dates_found": [],
    }
    scores = score_geo(empty)
    assert scores["total"] < 20, f"空内容应低于20分，实际: {scores['total']}"
    assert scores["grade"].startswith("F"), f"空内容应为F级"


@test("评分引擎：理想内容返回高分")
def test_perfect_content_scores_high():
    perfect = {
        "url": "https://test.com/article",
        "success": True,
        "title": "2026年AI趋势深度分析报告 — 基于1000家企业调研数据",
        "meta_description": "本文基于1000家企业调研，深入分析2026年AI技术趋势，包含独家数据和行业洞察，为企业AI战略提供决策参考。",
        "headings": [
            {"level": 1, "text": "2026年AI趋势深度分析报告"},
            {"level": 2, "text": "调研方法论"},
            {"level": 2, "text": "核心发现"},
            {"level": 2, "text": "行业分析"},
            {"level": 2, "text": "建议与展望"},
            {"level": 3, "text": "金融行业"},
            {"level": 3, "text": "医疗行业"},
        ],
        "paragraphs": [
            "根据IDC最新报告，2026年全球AI支出预计达到2.59万亿美元。我们的调研覆盖了1000家企业，发现78%的企业已经在生产环境中使用AI。",
            "数据显示，AI技术的采用率同比增长了45%。其中金融行业领先，采纳率达到92%。医疗行业紧随其后，采纳率为85%。",
            "哈佛商业评论2025年的研究指出，成功部署AI的企业平均利润率提升了12.5个百分点。我们的数据进一步验证了这一发现。",
            "本次调研的独特贡献在于首次量化了AI Agent对组织效能的影响。结果显示，引入Agent工作流的企业，决策速度平均提升了3.2倍。",
            "Bloomberg Intelligence分析师John Smith表示：'2026年是AI从实验走向规模化的转折点。'这一判断得到了我们数据的支持。",
        ] * 3,  # 15个段落
        "lists": [
            ["金融行业采纳率: 92%", "医疗行业采纳率: 85%", "制造业采纳率: 67%", "零售业采纳率: 58%"],
            ["第一步：建立AI战略委员会", "第二步：评估现有数据基础设施", "第三步：选择试点场景"],
            ["1. Agent化转型是最大趋势", "2. 多模态能力显著提升", "3. 合规要求日趋严格"],
        ],
        "word_count": 2500,
        "structured_data": [
            {"@type": "Article", "headline": "2026年AI趋势深度分析报告", "author": {"@type": "Person", "name": "张三"}},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": "2026年AI趋势有哪些？"}]},
        ],
        "entities": [{"name": "IDC", "type": "Organization"}, {"name": "John Smith", "type": "Person"}] * 10,
        "links_internal": [{"url": "https://test.com/about", "text": "关于我们"}] * 12,
        "links_external": [{"url": "https://hbr.org/report", "text": "Harvard Business Review"}] * 10,
        "images": [{"src": "img1.png", "alt": "2026年AI支出趋势图"}] * 5,
        "dates_found": ["2026-06-01", "2026-05-15", "2025-12-01"],
    }
    scores = score_geo(perfect)
    assert scores["total"] >= 70, f"优质内容应≥70分，实际: {scores['total']}"
    assert scores["entity_clarity"] >= 15, f"高实体清晰度: {scores['entity_clarity']}"
    assert scores["citation_worthiness"] >= 15, f"高可引用性: {scores['citation_worthiness']}"
    assert scores["content_structure"] >= 15, f"高结构分: {scores['content_structure']}"


@test("评分引擎：各维度满分不超过上限")
def test_score_dimensions_capped():
    """确保每个维度不超过其上限"""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from src.utils import score_geo

    huge = {
        "url": "https://test.com", "success": True,
        "title": "T" * 200, "meta_description": "D" * 320,
        "headings": [{"level": i, "text": "H"} for i in range(1, 4)] * 10,
        "paragraphs": ["据统计，全球AI市场在2026年达到前所未有的高度。根据权威研究..." * 20],
        "lists": [["item1", "item2", "item3"]] * 10,
        "word_count": 10000,
        "structured_data": [{"@type": t} for t in
            ["Article", "Organization", "FAQPage", "Product", "Review", "BreadcrumbList"]] * 3,
        "entities": [{"name": f"E{i}", "type": "Org"} for i in range(100)],
        "links_internal": [{"url": "/"} for _ in range(50)],
        "links_external": [{"url": "https://gov.cn"} for _ in range(50)],
        "images": [{"src": f"i{i}.png", "alt": f"alt{i}"} for i in range(20)],
        "dates_found": ["2026-06-01"] * 20,
    }
    scores = score_geo(huge)
    assert scores["entity_clarity"] <= 25, f"Entity超出: {scores['entity_clarity']}"
    assert scores["citation_worthiness"] <= 25, f"Citation超出: {scores['citation_worthiness']}"
    assert scores["content_structure"] <= 20, f"Structure超出: {scores['content_structure']}"
    assert scores["freshness_signals"] <= 15, f"Freshness超出: {scores['freshness_signals']}"
    assert scores["authority_signals"] <= 15, f"Authority超出: {scores['authority_signals']}"
    assert scores["total"] <= 100, f"总分超出: {scores['total']}"


# ═══════════════════════════════════════════════════════════════
# 层级 A2: 单元测试 — 工具函数
# ═══════════════════════════════════════════════════════════════


@test("HTTP抓取：成功获取真实网页")
def test_fetch_real_page():
    result = fetch_url("https://httpbin.org/html")
    if result["success"]:
        assert len(result["title"]) > 0, "应有标题"
        assert result["word_count"] > 0, "应有内容"
    else:
        # httpbin 可能不通，跳过
        print(f"    (网络不可用，跳过: {result.get('error', '')})")


@test("HTTP抓取：错误状态码处理")
def test_fetch_404():
    result = fetch_url("https://httpbin.org/status/404")
    # httpbin 可能超时或返回非预期状态码
    if result.get("error"):
        print(f"    (外部服务异常: {result['error'][:50]}，跳过)")
        return
    if result["status_code"] and result["status_code"] >= 400:
        # 任何 4xx/5xx 都应标记为不成功
        assert not result["success"], f"HTTP {result['status_code']} 应标记为不成功"


@test("缓存：写入和读取")
def test_cache_works():
    cache_set("test_key", {"value": 42})
    cached = cache_get("test_key")
    assert cached is not None, "缓存应命中"
    assert cached["value"] == 42, f"缓存值应为42，实际: {cached['value']}"


@test("缓存：过期后返回None")
def test_cache_expiry():
    import time
    from src.utils import _cache, CACHE_TTL
    cache_set("expire_key", "data")
    # 手动回退时间戳模拟过期
    _cache["expire_key"] = (time.time() - CACHE_TTL - 10, "data")
    assert cache_get("expire_key") is None, "过期缓存应返回None"


# ═══════════════════════════════════════════════════════════════
# 层级 B: 集成测试 — 工具函数组合
# ═══════════════════════════════════════════════════════════════

QUICK = "--quick" in sys.argv


@test("引用检测：返回结构正确")
def test_citation_structure():
    if QUICK:
        print("    (快速模式，跳过)")
        return
    result = check_citation("OpenAI", "AI")
    assert "brand" in result, "应有brand字段"
    assert result["brand"] == "OpenAI"
    assert "engines" in result, "应有engines字段"
    assert "overall_presence_score" in result, "应有overall_presence_score"
    assert "summary" in result, "应有summary"
    # 每个引擎都有完整字段
    for ek in ["chatgpt", "claude", "gemini", "perplexity"]:
        engine = result["engines"].get(ek, {})
        assert "mentioned" in engine, f"{ek}应有mentioned"
        assert "mention_count_estimate" in engine
        assert "sentiment" in engine


@test("内容评分：返回结构正确")
def test_scorer_structure():
    if QUICK:
        print("    (快速模式，跳过)")
        return
    result = score_content("https://example.com")
    assert "total" in result
    assert "grade" in result
    assert "breakdown" in result
    assert "entity_clarity" in result
    assert "citation_worthiness" in result
    assert "content_structure" in result
    assert "freshness_signals" in result
    assert "authority_signals" in result


@test("竞品分析：排名和矩阵正确")
def test_competitor_matrix():
    if QUICK:
        print("    (快速模式，跳过)")
        return
    result = competitor_gap("Notion", ["Confluence", "Evernote"], "productivity")
    assert "matrix" in result
    assert "my_rank" in result
    assert "gaps" in result
    assert len(result["matrix"]) == 3, f"应有3个品牌的矩阵，实际: {len(result['matrix'])}"
    # 矩阵中的品牌
    brands_in_matrix = {m["brand"] for m in result["matrix"]}
    assert "Notion" in brands_in_matrix


@test("品牌监控：保存和读取快照")
def test_monitor_snapshot():
    if QUICK:
        print("    (快速模式，跳过)")
        return
    # 清空之前的测试数据
    import glob
    monitor_dir = os.path.join(os.path.dirname(__file__), "monitor_data")
    if os.path.exists(monitor_dir):
        for f in glob.glob(os.path.join(monitor_dir, "test_brand_*.json")):
            os.remove(f)

    result = track_brand("test_brand_xyz")
    assert result["snapshots_count"] == 1
    assert result["current_score"] is not None

    # 再次追踪
    result2 = track_brand("test_brand_xyz")
    assert result2["snapshots_count"] >= 1

    # 读取趋势
    trend = get_trend("test_brand_xyz")
    assert trend["snapshots_count"] >= 1


@test("AI可见度报告：综合结构正确")
def test_visibility_report():
    if QUICK:
        print("    (快速模式，跳过)")
        return
    result = analyze_ai_visibility("Notion", ["https://www.notion.so"])
    assert "citation_score" in result
    assert "avg_content_geo_score" in result
    assert "composite_score" in result
    assert "verdict" in result


# ═══════════════════════════════════════════════════════════════
# 层级 C: MCP Server 协议测试
# ═══════════════════════════════════════════════════════════════


@test("MCP Server：初始化成功")
def test_mcp_server_init():
    from server import mcp
    assert mcp.name == "GEO Optimizer", f"Server名称应为GEO Optimizer"
    import asyncio
    async def check():
        tools = await mcp.list_tools()
        assert len(tools) == 6, f"应有6个工具，实际: {len(tools)}"
        resources = await mcp.list_resources()
        assert len(resources) == 2, f"应有2个资源，实际: {len(resources)}"
        prompts = await mcp.list_prompts()
        assert len(prompts) == 2, f"应有2个提示词，实际: {len(prompts)}"
    asyncio.run(check())


@test("MCP资源：best-practices 内容正确")
def test_resource_best_practices():
    import asyncio
    from server import mcp
    async def check():
        resources = await mcp.list_resources()
        uris = [str(r.uri) for r in resources]
        assert any("best-practices" in u for u in uris), f"缺少 best-practices，现有: {uris}"
        assert any("checklist" in u for u in uris), f"缺少 checklist，现有: {uris}"
    asyncio.run(check())


@test("MCP工具：签名参数正确")
def test_tool_signatures():
    import asyncio
    from server import mcp
    async def check():
        tools = await mcp.list_tools()
        tool_names = {t.name for t in tools}
        expected = {
            "geo_check_citation", "geo_content_score",
            "geo_competitor_gap", "geo_brand_monitor",
            "geo_brand_trend", "geo_ai_visibility",
        }
        missing = expected - tool_names
        extra = tool_names - expected
        assert not missing, f"缺少工具: {missing}"
        assert not extra, f"多余工具: {extra}"
    asyncio.run(check())


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    verbose = "--verbose" in sys.argv

    print("=" * 60)
    print("🧪 GEO MCP Server — 测试套件")
    print("=" * 60)
    if QUICK:
        print("⚡ 快速模式：跳过网络相关测试")
    print()

    start = time.time()

    # 执行所有以 test_ 开头的函数
    test_funcs = [
        (name, fn) for name, fn in sorted(globals().items())
        if name.startswith("test_") and callable(fn)
    ]
    for name, fn in test_funcs:
        fn()

    elapsed = time.time() - start

    print()
    print("=" * 60)
    total = PASS + FAIL
    print(f"📊 结果: {PASS}/{total} 通过, {FAIL} 失败 ({elapsed:.1f}s)")

    if FAIL == 0:
        print("🎉 全部通过！Server 可以上线了。")
    else:
        print(f"⚠️  有 {FAIL} 个测试失败，请修复后重试。")

    sys.exit(0 if FAIL == 0 else 1)
