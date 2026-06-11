# 我做了个 GEO MCP Server，免费检测你的品牌在 ChatGPT/Claude 中的可见度

## 一个让我失眠的问题

上个月我问 ChatGPT："推荐一个养生科普平台"。

它推荐了 3 个网站。没有我的。

我的网站运营了半年，每天更新，SEO 排名也不差。但在 AI 眼里——我不存在。

查了一圈资料，我发现了一个新词：**GEO（Generative Engine Optimization，生成式引擎优化）**。

和 SEO 不同，GEO 不是让搜索引擎找到你，而是**让 AI 推荐你**。

---

## 为什么 GEO 比 SEO 更重要？

一组数据：

> - 92% 的美国开发者每天用 AI 工具写代码
> - 41% 的代码已经是 AI 生成的
> - 到 2026 年底，60% 的新代码将由 AI 生成
> - AI 搜索和推荐的流量正在以每月 15%+ 的速度增长

人们不再"搜"，而是**问 AI**。

你的客户问 Claude "最好的项目管理工具有哪些"，问 ChatGPT "推荐一款适合小团队的 CRM"——**你的品牌出现在答案里吗？**

---

## 所以我做了这个工具

GEO MCP Server，一个挂在 Claude Code / Cursor / Windsurf 下的 AI 工具。

### 它能做什么？

**🔍 检测品牌 AI 引用**
输入你的品牌名，自动搜索 ChatGPT / Claude / Gemini / Perplexity 生态中是否有你的品牌被引用、被讨论。

**📊 GEO 内容评分**
输入你的网页 URL，5 个维度打分（0-100）：

| 维度 | 满分 | 评估什么 |
|------|------|---------|
| Entity Clarity | 25 | Schema 结构化数据、实体定义 |
| Citation Worthiness | 25 | 是否有可被 AI 引用的数据、统计、独特观点 |
| Content Structure | 20 | 标题层级、列表、FAQ |
| Freshness | 15 | 更新频率、时效性 |
| Authority | 15 | 外部引用、作者资质、HTTPS |

**🏆 竞品 AI 引用对比**
对比你和竞品在 4 大 AI 引擎中的引用差距。谁排第一？差在哪？

**📈 品牌引用趋势**
每周追踪一次，看你的 GEO 优化有没有效果。

---

## 一个真实例子

我分析了自己的养生科普站：

```
GEO 总分: 67/100  B 级

Entity:    14/25 ██████████████░░░░░░░░░░
Citation:  18/25 ██████████████████░░░░░░
Structure: 16/20 ████████████████░░░░░░░░
Freshness: 12/15 ████████████░░░░░░░░░░░░
Authority:  7/15 ███████░░░░░░░░░░░░░░░░░ ← 最大短板
```

发现两个致命问题：
1. 首页自称"养生平台"，10 篇文章没有一篇讲养生
2. 无作者资质、无外链引用、无图片 ALT

AI 看到这样的网站，根本不会把它归类为"养生权威来源"。

---

## 怎么用？

### 安装

```bash
pip install geo-mcp-optimizer
```

### Claude Desktop 配置

```json
{
  "mcpServers": {
    "geo-optimizer": {
      "command": "python",
      "args": ["geo-mcp-optimizer 的路径/server.py"]
    }
  }
}
```

### 然后直接对话

```
"检测 Notion 在 AI 引擎中的引用情况"
"分析 mysite.com 的 GEO 评分"
"对比飞书和钉钉在 AI 引用上的差距"
```

---

## 定价

| Tier | 价格 | 适合 |
|------|------|------|
| **Free** | ¥0 | 每天 50 次查询，基础功能 |
| **Pro** | ¥149/年 | 无限查询，竞品分析，趋势追踪 |
| **Team** | ¥399/年 | 5 席位，优先支持 |

---

## 开源

GitHub: https://github.com/chenzhi1985/geo-mcp-server

PyPI: https://pypi.org/project/geo-mcp-optimizer/

购买 Pro: https://www.reedsail.com/geo-pro/

---

**你的品牌在 AI 眼里存在吗？装一个看看。**

*如果觉得有用，帮我点个 Star ⭐*
