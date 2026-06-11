<?php
define('WP_USE_THEMES', false);
require_once '/var/www/www.reedsail.com/wp-load.php';

$content = <<<HTML
<meta http-equiv="refresh" content="0;url=https://www.reedsail.com/geo-pro/">
<div style="background:linear-gradient(135deg,#0d2818,#0d2137);border:2px solid #3fb950;border-radius:12px;padding:24px;text-align:center;font-family:-apple-system,BlinkMacSystemFont,sans-serif;margin:20px 0;">
  <h2 style="color:#3fb950;margin:0 0 8px;font-size:24px;">🌐 GEO MCP Server</h2>
  <p style="color:#c9d1d9;font-size:16px;margin:0 0 16px;">生成式引擎优化 — 检测品牌在 ChatGPT/Claude/Gemini/Perplexity 中的 AI 可见度</p>
  <p style="color:#8b949e;font-size:14px;">5 维度 GEO 评分 (0-100) · 竞品 AI 引用对比 · 品牌引用趋势追踪</p>
  <div style="margin:20px 0;">
    <a href="https://www.reedsail.com/geo-pro/" style="display:inline-block;background:#3fb950;color:#fff;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:600;font-size:16px;margin:4px;">📥 立即下载</a>
    <a href="https://www.reedsail.com/geo-pro/docs" style="display:inline-block;background:#30363d;color:#c9d1d9;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:600;font-size:16px;margin:4px;">📖 产品文档</a>
  </div>
  <p style="color:#8b949e;font-size:12px;margin:16px 0 0;">pip install geo-mcp-optimizer | Free 版免费 · Pro ¥149/年 · Team ¥399/年</p>
</div>
<script>setTimeout(function(){ window.location.href='https://www.reedsail.com/geo-pro/'; }, 3000);</script>
HTML;

wp_update_post([
    'ID' => 319,
    'post_content' => $content,
]);

echo "Post 319 updated — auto-redirects to geo-pro after 3 seconds\n";
