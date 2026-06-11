# [分享] 做了个 GEO MCP Server — 检测你的品牌在 ChatGPT/Claude 中是否被引用

今年年初发现一个事：我运营了半年的 WordPress 站，SEO 排名还不错，但问 ChatGPT "推荐一个 XX 平台"的时候，从来不推荐我。

查了圈资料才知道有个新概念叫 **GEO (Generative Engine Optimization)** ——不是让搜索引擎找到你，而是让 AI 推荐你。

然后我发现市面上几乎没几个 GEO 工具，就自己撸了一个。

---

## 做了什么

一个 MCP Server（挂在 Claude Code / Cursor / Windsurf 下面），6 个工具：

- `geo_check_citation` — 检测品牌在 ChatGPT/Claude/Gemini/Perplexity 中的引用存在
- `geo_content_score` — 5 维度 GEO 评分 (Entity/Citation/Structure/Freshness/Authority, 总分 100)
- `geo_competitor_gap` — 竞品 AI 引用差距分析
- `geo_brand_monitor` — 品牌引用趋势追踪
- `geo_brand_trend` — 历史趋势查询
- `geo_ai_visibility` — 综合 AI 可见度报告

还有 2 个内置资源 `geo://best-practices` 和 `geo://checklist`。

---

## 技术栈

- Python + FastMCP (MCP SDK)
- Bing/DuckDuckGo 双层搜索引擎（自动降级）
- 自定义 GEO 评分引擎（启发式 + 结构化数据解析）
- License Key 系统 (HMAC-SHA256)
- 微信支付 + x402 USDC 链上支付

---

## 安装

```bash
pip install geo-mcp-optimizer
```

Claude Desktop 加个配置就行。

---

## 定价

Free — 每天 50 次
Pro — ¥149/年（无限 + 竞品分析 + 趋势）
Team — ¥399/年（5 席位）

---

GitHub: https://github.com/chenzhi1985/geo-mcp-server
PyPI: https://pypi.org/project/geo-mcp-optimizer/
购买: https://www.reedsail.com/geo-pro/

---

欢迎 star / 提 issue / 吐槽。
