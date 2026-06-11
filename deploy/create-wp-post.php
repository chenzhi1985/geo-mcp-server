<?php
/**
 * 在 WordPress "软件下载" 分类下创建 GEO MCP Server 文章
 * 运行: sudo php create-wp-post.php
 */
define('WP_USE_THEMES', false);
require_once '/var/www/www.reedsail.com/wp-load.php';

// 找软件下载分类
$cats = get_categories(['hide_empty' => false]);
$target_id = null;
foreach ($cats as $cat) {
    if (strpos($cat->name, '软件') !== false || strpos($cat->name, '下载') !== false) {
        $target_id = $cat->term_id;
        echo "Found: ID={$cat->term_id} Name={$cat->name} Slug={$cat->slug}\n";
    }
}

if (!$target_id) {
    echo "ERROR: 软件下载 category not found. Available categories:\n";
    foreach ($cats as $cat) {
        echo "  ID={$cat->term_id} Name={$cat->name}\n";
    }
    exit(1);
}

// 检查是否已有同标题文章
$existing = get_posts([
    'title' => 'GEO MCP Server',
    'post_type' => 'post',
    'post_status' => 'any',
    'numberposts' => 1,
]);
if (!empty($existing)) {
    echo "⚠️  Post already exists: ID={$existing[0]->ID}\n";
    echo "   URL: " . get_permalink($existing[0]->ID) . "\n";
    exit(0);
}

// 文章内容
$content = <<<HTML
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
HTML;

$post_id = wp_insert_post([
    'post_title'    => '🌐 GEO MCP Server — 生成式引擎优化工具',
    'post_content'  => $content,
    'post_status'   => 'publish',
    'post_category' => [$target_id],
    'post_type'     => 'post',
]);

if ($post_id) {
    echo "✅ Post created! ID={$post_id}\n";
    echo "   Category page: https://www.reedsail.com/category/软件下载\n";
    echo "   Post URL: " . get_permalink($post_id) . "\n";
} else {
    echo "❌ Failed to create post\n";
}
