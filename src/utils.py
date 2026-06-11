"""
GEO MCP Server — 工具函数库
内容抓取、结构化数据提取、GEO评分算法
"""
from __future__ import annotations

import re
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Any
from urllib.parse import urlparse, urljoin, quote_plus
from collections import Counter

import httpx
from bs4 import BeautifulSoup, Tag


# ── HTTP 客户端 ──────────────────────────────────────────────
_client: Optional[httpx.Client] = None

def get_client(timeout: int = 15) -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/130.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            },
        )
    return _client


# ── 内容抓取 ──────────────────────────────────────────────────

def fetch_url(url: str) -> dict[str, Any]:
    """抓取 URL 并返回解析后的内容"""
    result = {
        "url": url,
        "success": False,
        "status_code": None,
        "title": "",
        "meta_description": "",
        "headings": [],
        "paragraphs": [],
        "lists": [],
        "word_count": 0,
        "structured_data": [],
        "entities": [],
        "links_internal": [],
        "links_external": [],
        "images": [],
        "dates_found": [],
        "error": None,
    }
    try:
        resp = get_client().get(url)
        result["status_code"] = resp.status_code
        if resp.status_code != 200:
            result["error"] = f"HTTP {resp.status_code}"
            return result
        result["success"] = True
        soup = BeautifulSoup(resp.text, "lxml")

        # 标题
        if soup.title:
            result["title"] = soup.title.get_text(strip=True)

        # Meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            result["meta_description"] = meta_desc["content"]

        # 标题层级
        for level in range(1, 7):
            for h in soup.find_all(f"h{level}"):
                text = h.get_text(strip=True)
                if text:
                    result["headings"].append({"level": level, "text": text[:200]})

        # 段落
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if text and len(text) > 40:
                result["paragraphs"].append(text[:500])

        # 列表项
        for ul in soup.find_all(["ul", "ol"]):
            items = [li.get_text(strip=True)[:200] for li in ul.find_all("li")]
            if items:
                result["lists"].append(items)

        # 字数
        body = soup.body
        if body:
            result["word_count"] = len(body.get_text(separator=" ", strip=True).split())

        # 结构化数据 (JSON-LD / Schema.org)
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                result["structured_data"].append(data)
            except (json.JSONDecodeError, TypeError):
                pass

        # 实体识别 (命名实体启发式提取)
        full_text = soup.body.get_text(separator=" ", strip=True) if soup.body else ""
        result["entities"] = _extract_entities(full_text)

        # 链接
        base_domain = urlparse(url).netloc
        for a in soup.find_all("a", href=True):
            href = urljoin(url, a["href"])
            parsed = urlparse(href)
            if parsed.scheme in ("http", "https"):
                link_info = {"url": href, "text": a.get_text(strip=True)[:100]}
                if parsed.netloc == base_domain:
                    result["links_internal"].append(link_info)
                else:
                    result["links_external"].append(link_info)

        # 图片
        for img in soup.find_all("img", src=True):
            result["images"].append({
                "src": urljoin(url, img["src"]),
                "alt": img.get("alt", ""),
            })

        # 日期
        date_patterns = [
            r"\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?",
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}",
        ]
        for pattern in date_patterns:
            found = re.findall(pattern, resp.text, re.IGNORECASE)
            result["dates_found"].extend(found)

    except httpx.RequestError as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = f"Parse error: {e}"

    return result


def _extract_entities(text: str) -> list[dict[str, Any]]:
    """启发式实体提取"""
    entities = []
    # 法人实体（公司、品牌）
    company_patterns = [
        r"([A-Z][a-z]+ (?:Inc|Corp|LLC|Ltd|Group|Company|Technologies|AI|Labs))",
        r"(字节跳动|阿里巴巴|腾讯|百度|华为|美团|京东|拼多多|网易|小米|OPPO|vivo)",
    ]
    for pattern in company_patterns:
        for match in re.finditer(pattern, text):
            entities.append({"name": match.group(1), "type": "Organization", "method": "regex"})

    # 人名
    person_pattern = r"([A-Z][a-z]+ [A-Z][a-z]+ (?:said|stated|reported|wrote|published|announced|according to))"
    for match in re.finditer(person_pattern, text[:5000]):
        name = match.group(1).rsplit(" ", 1)[0]
        entities.append({"name": name, "type": "Person", "method": "regex"})

    return entities[:50]


# ── GEO 评分引擎 ──────────────────────────────────────────────

def score_geo(content: dict[str, Any]) -> dict[str, Any]:
    """
    对抓取的内容进行 GEO 评分（0-100分）

    五个维度：
    - Entity Clarity (25pts): 实体定义清晰度
    - Citation Worthiness (25pts): 可引用性
    - Content Structure (20pts): 内容结构
    - Freshness Signals (15pts): 时效性信号
    - Authority Signals (15pts): 权威性信号
    """
    scores = {}

    # 1. Entity Clarity (25pts)
    entity_score = 0
    # Schema.org 结构化数据
    if content["structured_data"]:
        entity_score += 10
        schemas = [s.get("@type", "") for s in content["structured_data"] if isinstance(s, dict)]
        unique_schemas = len(set(schemas))
        entity_score += min(unique_schemas * 3, 9)
    # 提取到的实体数量
    entity_count = len(content["entities"])
    if entity_count >= 10:
        entity_score += 3
    elif entity_count >= 5:
        entity_score += 1
    # Meta description 存在且长度适中
    meta_len = len(content["meta_description"])
    if 100 <= meta_len <= 320:
        entity_score += 3
    elif meta_len > 0:
        entity_score += 1
    scores["entity_clarity"] = min(entity_score, 25)

    # 2. Citation Worthiness (25pts)
    citation_score = 0
    full_text = " ".join(content["paragraphs"])
    # 统计数据
    stats_count = len(re.findall(r"\d+\.?\d*%|\d+/\d+|≈\d+|\$\d+|¥\d+|\d+ million|\d+ billion", full_text))
    if stats_count >= 10:
        citation_score += 10
    elif stats_count >= 5:
        citation_score += 6
    elif stats_count >= 1:
        citation_score += 3
    # 引用/来源
    cite_markers = len(re.findall(r"(according to|reported by|published in|source:|cited from|参考|来源)", full_text, re.I))
    if cite_markers >= 5:
        citation_score += 7
    elif cite_markers >= 2:
        citation_score += 4
    elif cite_markers >= 1:
        citation_score += 2
    # 独特数据信号（原创研究标记）
    unique_signals = len(re.findall(r"(survey|study|research|analysis|report|found that|调查|研究|发现|数据显示)", full_text, re.I))
    if unique_signals >= 5:
        citation_score += 8
    elif unique_signals >= 2:
        citation_score += 4
    scores["citation_worthiness"] = min(citation_score, 25)

    # 3. Content Structure (20pts)
    structure_score = 0
    headings = content["headings"]
    # 标题层级
    h1_count = sum(1 for h in headings if h["level"] == 1)
    h2_count = sum(1 for h in headings if h["level"] == 2)
    if h1_count == 1:
        structure_score += 5
    elif h1_count > 0:
        structure_score += 2
    if h2_count >= 3:
        structure_score += 5
    elif h2_count >= 1:
        structure_score += 2
    # 列表
    list_count = len(content["lists"])
    if list_count >= 3:
        structure_score += 5
    elif list_count >= 1:
        structure_score += 2
    # 字数
    wc = content["word_count"]
    if wc >= 1500:
        structure_score += 3
    elif wc >= 500:
        structure_score += 1
    # FAQ schema
    has_faq = any(
        isinstance(s, dict) and
        (s.get("@type") == "FAQPage" or "Question" in str(s))
        for s in content["structured_data"]
    )
    if has_faq:
        structure_score += 2
    scores["content_structure"] = min(structure_score, 20)

    # 4. Freshness Signals (15pts)
    freshness_score = 0
    dates = content["dates_found"]
    if dates:
        freshness_score += 5
        # 检查日期是否在最近6个月内
        now = datetime.now()
        recent = False
        for d in dates:
            try:
                # 尝试多种日期格式
                for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日", "%b %d, %Y", "%B %d, %Y"]:
                    try:
                        dt = datetime.strptime(d, fmt)
                        if (now - dt).days < 180:
                            recent = True
                        break
                    except ValueError:
                        continue
            except Exception:
                pass
        if recent:
            freshness_score += 7
        else:
            freshness_score += 2
    # 更新时间标记
    update_markers = len(re.findall(r"(updated|last modified|published|更新|发布)\s*:?\s*\d{4}", full_text, re.I))
    if update_markers > 0:
        freshness_score += 3
    scores["freshness_signals"] = min(freshness_score, 15)

    # 5. Authority Signals (15pts)
    authority_score = 0
    # 外部链接（引用权威来源）
    ext_links = len(content["links_external"])
    if ext_links >= 10:
        authority_score += 5
    elif ext_links >= 3:
        authority_score += 2
    # 内部链接深度
    int_links = len(content["links_internal"])
    if int_links >= 10:
        authority_score += 3
    elif int_links >= 5:
        authority_score += 1
    # 图片 ALT 文本
    images_with_alt = sum(1 for img in content["images"] if img.get("alt"))
    if images_with_alt >= 3:
        authority_score += 3
    elif images_with_alt >= 1:
        authority_score += 1
    # SSL (https)
    if content["url"].startswith("https://"):
        authority_score += 2
    # About / Contact 页面的链接信号
    about_signals = len(re.findall(r"(about|contact|author|bio|关于|联系|作者)", str(content["links_internal"]), re.I))
    if about_signals >= 3:
        authority_score += 2
    elif about_signals >= 1:
        authority_score += 1
    scores["authority_signals"] = min(authority_score, 15)

    total = sum(scores.values())
    scores["total"] = min(total, 100)

    # 评级
    if scores["total"] >= 80:
        grade = "A — 极高的AI引用潜力"
    elif scores["total"] >= 65:
        grade = "B — 良好的AI引用潜力，有几个维度可以优化"
    elif scores["total"] >= 50:
        grade = "C — 中等，需要在薄弱维度重点改进"
    elif scores["total"] >= 35:
        grade = "D — AI引用潜力不足，建议全面优化"
    else:
        grade = "F — 很难被AI引用，需要重建内容策略"

    scores["grade"] = grade
    scores["breakdown"] = _generate_recommendations(scores, content)

    return scores


def _generate_recommendations(scores: dict, content: dict) -> list[dict[str, Any]]:
    """根据评分生成优化建议"""
    recommendations = []

    if scores["entity_clarity"] < 15:
        recommendations.append({
            "dimension": "entity_clarity",
            "priority": "high" if scores["entity_clarity"] < 10 else "medium",
            "issue": "实体定义不够清晰，AI难以理解页面主题",
            "actions": [
                "添加 Schema.org 结构化数据（Organization/Article/FAQPage）",
                "在首段明确定义核心实体（品牌/产品/人物）",
                "优化 Meta Description 到 120-160 字符",
                "使用清晰的品牌名称和专有名词",
            ],
        })

    if scores["citation_worthiness"] < 15:
        recommendations.append({
            "dimension": "citation_worthiness",
            "priority": "high" if scores["citation_worthiness"] < 10 else "medium",
            "issue": "内容缺乏可引用的数据点和独特见解",
            "actions": [
                "加入统计数据、百分比、具体数字",
                "引用行业报告或原创研究",
                "提供独特的观点或分析框架",
                "使用「根据XX研究」「数据显示」等可被引用的句式",
                "创建原创调查或实验数据",
            ],
        })

    if scores["content_structure"] < 12:
        recommendations.append({
            "dimension": "content_structure",
            "priority": "medium",
            "issue": "内容结构不利于AI解析和引用",
            "actions": [
                "确保有且仅有一个 H1 标题",
                "使用 H2/H3 建立清晰的层级结构（至少3个H2）",
                "添加有序/无序列表整理信息",
                "加入 FAQ 结构化数据",
                "目标字数 1500+ 以保证内容深度",
            ],
        })

    if scores["freshness_signals"] < 9:
        recommendations.append({
            "dimension": "freshness_signals",
            "priority": "medium",
            "issue": "内容时效性信号不足，AI可能认为信息过时",
            "actions": [
                "添加明确的发布日期和最近更新日期",
                "每季度更新内容并标注更新时间",
                "在标题或首段加入年份（如「2026年」）",
                "定期发布新内容并建立内容更新日历",
            ],
        })

    if scores["authority_signals"] < 9:
        recommendations.append({
            "dimension": "authority_signals",
            "priority": "medium" if scores["authority_signals"] >= 5 else "high",
            "issue": "权威性信号不足，AI可能不信任此内容",
            "actions": [
                "引用权威外部来源并添加链接",
                "添加作者简介和资质说明",
                "确保所有图片有描述性 ALT 文本",
                "添加 About/Contact 页面",
                "获取来自权威网站的 backlink",
                "使用 HTTPS",
            ],
        })

    return recommendations


# ── 搜索引擎模拟 ──────────────────────────────────────────────

# AI 引擎的搜索特征
AI_ENGINES = {
    "chatgpt": {
        "name": "ChatGPT / OpenAI",
        "search_suffix": "site:openai.com OR site:community.openai.com",
        "citation_markers": ["chatgpt", "openai", "gpt-4", "gpt-5"],
    },
    "claude": {
        "name": "Claude / Anthropic",
        "search_suffix": "site:anthropic.com OR site:claude.ai",
        "citation_markers": ["claude", "anthropic", "claude.ai"],
    },
    "gemini": {
        "name": "Gemini / Google AI",
        "search_suffix": "site:blog.google OR site:deepmind.google",
        "citation_markers": ["gemini", "google ai", "deepmind"],
    },
    "perplexity": {
        "name": "Perplexity AI",
        "search_suffix": "site:perplexity.ai",
        "citation_markers": ["perplexity", "perplexity ai"],
    },
}


def _search_bing(query: str) -> list[dict[str, str]]:
    """Bing 搜索（DuckDuckGo 的后备方案）"""
    bing_url = f"https://www.bing.com/search?q={quote_plus(query)}"
    resp = get_client(timeout=10).get(bing_url)
    if resp.status_code != 200:
        return []
    soup = BeautifulSoup(resp.text, "lxml")
    results = []
    for item in soup.find_all("li", class_="b_algo"):
        h2 = item.find("h2")
        title_link = h2.find("a", href=True) if h2 else None
        snippet_el = item.find(class_="b_caption")
        url_el = item.find(class_="b_attribution")
        title = title_link.get_text(strip=True) if title_link else ""
        snippet = snippet_el.get_text(strip=True) if snippet_el else ""
        url = url_el.get_text(strip=True) if url_el else ""
        if title:
            results.append({"title": title, "snippet": snippet, "url": url})
    return results


def _search_ddg(query: str, retries: int = 2) -> list[dict[str, str]]:
    """执行 DuckDuckGo HTML 搜索，失败自动降级到 Bing"""
    import time as _time
    for attempt in range(retries + 1):
        ddg_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        resp = get_client(timeout=10).get(ddg_url)
        if resp.status_code in (202, 429):
            if attempt < retries:
                _time.sleep(2.0 * (attempt + 1))
                continue
            # DuckDuckGo 限速 → 降级到 Bing
            return _search_bing(query)
        if resp.status_code != 200:
            return _search_bing(query)
        soup = BeautifulSoup(resp.text, "lxml")
        results = []
        for result_div in soup.find_all("div", class_="result"):
            title_el = result_div.find("a", class_="result__a")
            snippet_el = result_div.find("a", class_="result__snippet")
            url_el = result_div.find("a", class_="result__url")
            title_text = title_el.get_text(strip=True) if title_el else ""
            snippet_text = snippet_el.get_text(strip=True) if snippet_el else ""
            url_text = url_el.get_text(strip=True) if url_el else ""
            if title_text or snippet_text:
                results.append({
                    "title": title_text,
                    "snippet": snippet_text,
                    "url": url_text,
                })
        return results
    return _search_bing(query)


def search_citations(brand: str, topic: Optional[str] = None) -> dict[str, Any]:
    """
    搜索品牌在各 AI 引擎中的引用情况

    通过两层搜索检测品牌是否被 AI 生态讨论/引用：
    1. 品牌名 + AI引擎关键词（宽搜索）
    2. 在 AI 平台官方域名内搜索（精准验证）
    """
    results = {
        "brand": brand,
        "topic": topic,
        "checked_at": datetime.now().isoformat(),
        "engines": {},
        "overall_presence_score": 0,
        "summary": "",
    }

    for engine_key, engine_info in AI_ENGINES.items():
        # 引擎间延迟，防止 DuckDuckGo 限速
        if engine_key != list(AI_ENGINES.keys())[0]:
            time.sleep(1.5)

        engine_result = {
            "engine": engine_info["name"],
            "mentioned": False,
            "mention_count_estimate": 0,
            "context": [],
            "top_urls": [],
            "sentiment": "neutral",
        }
        try:
            # 宽搜索：品牌 + AI引擎名 + 话题
            broad_query = f'"{brand}" {engine_info["citation_markers"][0]}'
            if topic:
                broad_query += f' {topic}'
            broad_results = _search_ddg(broad_query)

            # 精准搜索：在 AI 平台官方域内搜索品牌
            narrow_query = f'"{brand}" {engine_info["search_suffix"]}'
            narrow_results = _search_ddg(narrow_query)

            # 合并结果
            all_results = broad_results + narrow_results
            # 去重
            seen_urls = set()
            unique_results = []
            for r in all_results:
                if r["url"] and r["url"] not in seen_urls:
                    seen_urls.add(r["url"])
                    unique_results.append(r)

            engine_result["mention_count_estimate"] = len(unique_results)
            engine_result["mentioned"] = len(unique_results) > 0

            # 提取上下文
            for r in unique_results[:5]:
                if r["snippet"]:
                    engine_result["context"].append(r["snippet"][:300])
                if r["url"]:
                    engine_result["top_urls"].append(r["url"])

            # 简单情感分析
            all_text = " ".join(engine_result["context"])
            positive = sum(1 for w in ["best", "top", "leading", "excellent", "推荐", "最佳", "powerful", "great", "amazing"]
                         if w in all_text.lower())
            negative = sum(1 for w in ["worst", "poor", "avoid", "差", "不推荐", "terrible", "broken", "useless"]
                         if w in all_text.lower())
            if positive > negative:
                engine_result["sentiment"] = "positive"
            elif negative > positive:
                engine_result["sentiment"] = "negative"

        except Exception as e:
            engine_result["error"] = str(e)

        results["engines"][engine_key] = engine_result

    # 整体引用指数（改进算法）
    mentioned_count = sum(1 for e in results["engines"].values() if e["mentioned"])
    total_mentions = sum(e["mention_count_estimate"] for e in results["engines"].values())
    positive_engines = sum(1 for e in results["engines"].values() if e["sentiment"] == "positive")

    results["overall_presence_score"] = min(100,
        mentioned_count * 15 +       # 每个被提及的引擎 +15
        positive_engines * 5 +       # 正向情感 +5
        min(total_mentions * 3, 40)  # 提及量（封顶40）
    )

    if results["overall_presence_score"] >= 70:
        results["summary"] = f"✅ {brand} 在 AI 生态中有较强的引用存在，建议维护并扩大优势"
    elif results["overall_presence_score"] >= 30:
        results["summary"] = f"⚠️ {brand} 在 AI 生态中有一定的引用，但仍有提升空间"
    else:
        results["summary"] = f"❌ {brand} 在 AI 生态中引用很少，建议从内容GEO优化入手"

    return results


# ── 缓存 ──────────────────────────────────────────────────────

_cache: dict[str, tuple[float, Any]] = {}
CACHE_TTL = 3600  # 1小时


def cache_get(key: str) -> Optional[Any]:
    entry = _cache.get(key)
    if entry and time.time() - entry[0] < CACHE_TTL:
        return entry[1]
    return None


def cache_set(key: str, value: Any) -> None:
    _cache[key] = (time.time(), value)
    # 清理过期缓存
    if len(_cache) > 100:
        expired = [k for k, v in _cache.items() if time.time() - v[0] > CACHE_TTL]
        for k in expired:
            del _cache[k]
