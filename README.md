# 🌐 GEO MCP Server — 生成式引擎优化工具

检测品牌在 AI 引擎（ChatGPT / Claude / Gemini / Perplexity）中的引用存在、评分内容 GEO 优化程度、分析竞品差距、追踪引用趋势。

专为 **Claude Code** 和 **MCP 兼容客户端** 设计。

---

## 🔗 快速链接

| 入口 | 地址 |
|------|------|
| 📦 **下载安装** | `pip install geo-mcp-optimizer` |
| 🛒 **购买 Pro** | [reedsail.com/geo-pro](https://www.reedsail.com/geo-pro/) |
| 📊 **管理面板** | [reedsail.com/geo-pro/admin](https://www.reedsail.com/geo-pro/admin) |
| 📖 **产品文档** | [reedsail.com/geo-pro/docs](https://www.reedsail.com/geo-pro/docs) |
| 💻 **GitHub** | [github.com/chenzhi1985/geo-mcp-server](https://github.com/chenzhi1985/geo-mcp-server) |
| 🐍 **PyPI** | [pypi.org/project/geo-mcp-optimizer](https://pypi.org/project/geo-mcp-optimizer/) |

---

## 🎯 功能

| 工具 | 功能 | 输入 |
|------|------|------|
| `geo_check_citation` | 检测品牌在4大AI引擎中的引用情况 | 品牌名 + 话题 |
| `geo_content_score` | 对网页进行GEO评分（0-100分，5维度） | URL + 关键词 |
| `geo_competitor_gap` | 竞品AI引用对比矩阵 | 品牌 + 竞品列表 |
| `geo_brand_monitor` | 记录品牌引用快照，追踪趋势 | 品牌名 |
| `geo_brand_trend` | 查看历史引用变化趋势 | 品牌名 |
| `geo_ai_visibility` | 综合AI可见度报告（引用+内容评分） | 品牌 + URL列表 |

### GEO 评分维度（内容评分 0-100）

| 维度 | 满分 | 评估内容 |
|------|------|---------|
| Entity Clarity | 25 | Schema.org、实体定义、Meta 信息 |
| Citation Worthiness | 25 | 统计数据、引用来源、独特见解 |
| Content Structure | 20 | 标题层级、列表、FAQ、字数 |
| Freshness Signals | 15 | 发布日期、更新频率 |
| Authority Signals | 15 | 外部链接、作者信息、HTTPS |

---

## 🚀 安装

```bash
# 1. 进入项目目录
cd geo-mcp-server

# 2. 安装依赖
pip install -r requirements.txt

# 3. 测试运行
python server.py
```

### 依赖
- Python ≥ 3.12
- `mcp` ≥ 1.20.0
- `httpx` ≥ 0.28.0
- `beautifulsoup4` ≥ 4.14.0
- `lxml` ≥ 6.0.0

---

## 🔌 配置 Claude Desktop

在 Claude Desktop 的 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "geo-optimizer": {
      "command": "python",
      "args": ["d:/项目管理/MCP Server/geo-mcp-server/server.py"]
    }
  }
}
```

**Mac/Linux 路径示例：**
```json
{
  "mcpServers": {
    "geo-optimizer": {
      "command": "python",
      "args": ["/path/to/geo-mcp-server/server.py"]
    }
  }
}
```

重启 Claude Desktop 后即可使用。

---

## 💬 使用示例

### 在 Claude Code 中对话

```
# 检测品牌 AI 引用
"帮我检测 Notion 这个品牌在 AI 引擎中的引用情况"

# 评分网页内容
"分析 https://mysite.com/blog/my-article 被 AI 引用的潜力"

# 竞品对比
"对比我们的品牌「飞书」和竞品「钉钉,企业微信」在 AI 中的引用差距"

# 综合诊断
"全面分析我的品牌 AI 可见度，关键页面是 https://mysite.com 和 https://mysite.com/blog"

# 查看最佳实践
"打开 geo://best-practices 查看 GEO 优化指南"

# 使用提示词
"用 geo_optimize 提示词帮我优化这篇文章"
```

### 在 Python 中直接调用

```python
from src.tools.citation import check_citation
from src.tools.scorer import score_content
from src.tools.competitor import competitor_gap

# 检测引用
result = check_citation("你的品牌名", topic="行业话题")
print(f"引用分: {result['overall_presence_score']}/100")

# 评分内容
result = score_content("https://example.com/article")
print(f"GEO评分: {result['total']}/100 — {result['grade']}")

# 竞品分析
result = competitor_gap("你的品牌", ["竞品A", "竞品B"], "行业话题")
print(f"排名: {result['my_rank']}")
```

---

## 📁 项目结构

```
geo-mcp-server/
├── server.py              # MCP Server 入口
├── src/
│   ├── __init__.py
│   ├── utils.py           # HTTP客户端、内容解析、GEO评分引擎
│   └── tools/
│       ├── __init__.py
│       ├── citation.py    # 引用检测 & AI可见度分析
│       ├── scorer.py      # 内容GEO评分
│       ├── competitor.py  # 竞品对比
│       └── monitor.py     # 品牌监控 & 趋势
├── monitor_data/          # 监控快照数据（自动生成）
├── requirements.txt
└── README.md
```

---

## 🛠️ 开发

```bash
# MCP Inspector 调试
npx @modelcontextprotocol/inspector python server.py

# SSE 模式（HTTP 调试）
python server.py --sse
```

---

## 💰 变现路径

本项目通过 MCP 生态平台变现：

| 平台 | 模式 | 分成 |
|------|------|------|
| [MCPize](https://mcpize.com) | 订阅制 | 85% |
| [AgenticMarket](https://agenticmarket.com) | Per-Call | 80-90% |
| [Polar.sh](https://polar.sh) | 独立售卖 | 96% |

---

## 📄 License

MIT
