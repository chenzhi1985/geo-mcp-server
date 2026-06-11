<?php
/**
 * 更新 WordPress Post 319 为产品着陆页
 */
define('WP_USE_THEMES', false);
require_once '/var/www/www.reedsail.com/wp-load.php';

$content = <<<HTML
<!-- wp:heading {"level":1} -->
<h1 class="wp-block-heading">🌐 GEO MCP Server — 生成式引擎优化工具</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><strong>检测你的品牌在 ChatGPT、Claude、Gemini、Perplexity 中的 AI 可见度。</strong>不是让搜索引擎找到你，而是让 AI 推荐你。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>用户不再"搜索"，而是<strong>问 AI</strong>。你的品牌出现在 AI 的回答里吗？GEO MCP Server 帮你找到答案。</p>
<!-- /wp:paragraph -->

<!-- wp:buttons -->
<div class="wp-block-buttons">
<!-- wp:button {"backgroundColor":"vivid-green-cyan","textColor":"white","fontSize":"medium"} -->
<div class="wp-block-button has-custom-font-size has-medium-font-size"><a class="wp-block-button__link has-white-color has-vivid-green-cyan-background-color has-text-color has-background wp-element-button" href="https://www.reedsail.com/geo-pro/" style="border-radius:8px"><strong>📥 立即下载</strong> — Free 版免费</a></div>
<!-- /wp:button -->
<!-- wp:button {"backgroundColor":"dark-gray","textColor":"white","fontSize":"medium"} -->
<div class="wp-block-button has-custom-font-size has-medium-font-size"><a class="wp-block-button__link has-white-color has-dark-gray-background-color has-text-color has-background wp-element-button" href="https://www.reedsail.com/geo-pro/docs">📖 产品文档</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->

<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity"/>
<!-- /wp:separator -->

<!-- wp:heading -->
<h2 class="wp-block-heading">🔍 六大核心工具</h2>
<!-- /wp:heading -->

<!-- wp:table -->
<figure class="wp-block-table"><table><thead><tr><th>工具</th><th>功能</th><th>使用场景</th></tr></thead><tbody><tr><td><code>geo_check_citation</code></td><td>检测品牌在 4 大 AI 引擎中的引用</td><td>"ChatGPT 推荐我的品牌吗？"</td></tr><tr><td><code>geo_content_score</code></td><td>5 维度 GEO 评分 (0-100)</td><td>"这篇文章会被 AI 引用吗？"</td></tr><tr><td><code>geo_competitor_gap</code></td><td>竞品 AI 引用差距分析</td><td>"我和竞品在 AI 上差多少？"</td></tr><tr><td><code>geo_brand_monitor</code></td><td>品牌引用趋势追踪</td><td>"本月 AI 引用有增长吗？"</td></tr><tr><td><code>geo_brand_trend</code></td><td>历史趋势查询</td><td>"过去6个月的变化？"</td></tr><tr><td><code>geo_ai_visibility</code></td><td>综合 AI 可见度报告</td><td>"全面诊断我的 AI 可见度"</td></tr></tbody></table></figure>
<!-- /wp:table -->

<!-- wp:heading -->
<h2 class="wp-block-heading">📊 GEO 评分维度</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>每个网页从 5 个维度评估被 AI 引用的潜力（总分 0-100）：</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li><strong>Entity Clarity (25分)</strong> — Schema.org 结构化数据、实体定义、Meta 信息</li>
<li><strong>Citation Worthiness (25分)</strong> — 统计数据、引用来源、独特数据见解</li>
<li><strong>Content Structure (20分)</strong> — 标题层级、列表结构、FAQ、内容丰富度</li>
<li><strong>Freshness Signals (15分)</strong> — 发布日期、更新频率</li>
<li><strong>Authority Signals (15分)</strong> — 外部引用、作者资质、HTTPS</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2 class="wp-block-heading">🚀 快速开始</h2>
<!-- /wp:heading -->

<!-- wp:code -->
<pre class="wp-block-code"><code>pip install geo-mcp-optimizer</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>在 Claude Desktop 的配置文件中添加：</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>{
  "mcpServers": {
    "geo-optimizer": {
      "command": "python",
      "args": ["server.py 的完整路径"]
    }
  }
}</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>重启 Claude Desktop，直接对话即可使用：<code>"检测飞书在 AI 引擎中的引用情况"</code></p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">💻 兼容客户端</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Claude Desktop · Claude Code · Cursor · Windsurf · Cline · Continue.dev · Zed · 任何 MCP 协议客户端</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">💰 定价</h2>
<!-- /wp:heading -->

<!-- wp:table -->
<figure class="wp-block-table"><table><thead><tr><th>Tier</th><th>价格</th><th>每日查询</th><th>竞品分析</th><th>趋势追踪</th></tr></thead><tbody><tr><td>Free</td><td>¥0</td><td>50</td><td>3 个</td><td>—</td></tr><tr><td>Pro</td><td>¥149/年</td><td>10,000</td><td>10 个</td><td>✅</td></tr><tr><td>Team</td><td>¥399/年</td><td>无限</td><td>50 个</td><td>✅</td></tr></tbody></table></figure>
<!-- /wp:table -->

<!-- wp:buttons -->
<div class="wp-block-buttons">
<!-- wp:button {"backgroundColor":"vivid-green-cyan","textColor":"white","style":{"border":{"radius":"8px"}},"fontSize":"large"} -->
<div class="wp-block-button has-custom-font-size has-large-font-size"><a class="wp-block-button__link has-white-color has-vivid-green-cyan-background-color has-text-color has-background wp-element-button" href="https://www.reedsail.com/geo-pro/" style="border-radius:8px"><strong>🛒 立即购买 Pro</strong> — ¥149/年</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->

<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity"/>
<!-- /wp:separator -->

<!-- wp:paragraph -->
<p>📧 联系：<a href="mailto:admin@reedsail.com">admin@reedsail.com</a> · 💻 <a href="https://github.com/chenzhi1985/geo-mcp-server">GitHub</a> · 📦 <a href="https://pypi.org/project/geo-mcp-optimizer/">PyPI</a></p>
<!-- /wp:paragraph -->
HTML;

// 更新文章
wp_update_post([
    'ID' => 319,
    'post_title' => 'GEO MCP Server — 生成式引擎优化工具 | AI可见度检测',
    'post_name' => 'geo-mcp-server',
    'post_content' => $content,
    'post_excerpt' => '检测品牌在 ChatGPT/Claude/Gemini 中的 AI 可见度。5维度 GEO 评分(0-100)，竞品分析，趋势追踪。pip install geo-mcp-optimizer。Free 版免费，Pro ¥149/年。',
    'meta_input' => [
        '_yoast_wpseo_title' => 'GEO MCP Server — 生成式引擎优化工具 | AI可见度检测',
        '_yoast_wpseo_metadesc' => '检测品牌在 ChatGPT/Claude/Gemini 中的 AI 可见度。5维度 GEO 评分，竞品分析，趋势追踪。pip install geo-mcp-optimizer。',
    ],
]);

// 更新 slug
wp_update_post([
    'ID' => 319,
    'post_name' => 'geo-mcp-server',
]);

$permalink = get_permalink(319);
echo "✅ Post 319 updated!\n";
echo "   Title: GEO MCP Server — 生成式引擎优化工具 | AI可见度检测\n";
echo "   Slug: geo-mcp-server\n";
echo "   URL: $permalink\n";
