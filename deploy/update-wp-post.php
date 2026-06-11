<?php
define('WP_USE_THEMES', false);
require_once '/var/www/www.reedsail.com/wp-load.php';

// 更新摘要
wp_update_post([
    'ID' => 319,
    'post_excerpt' => '生成式引擎优化工具 — 检测品牌在 ChatGPT/Claude/Gemini 中的 AI 可见度。5维度 GEO 评分，竞品分析，趋势追踪。pip install geo-mcp-optimizer',
]);

// 重定向到 geo-pro
update_post_meta(319, '_redirect_url', 'https://www.reedsail.com/geo-pro/');

echo "Updated post 319\n";
echo "Post URL: " . get_permalink(319) . " (will redirect to geo-pro)\n";
echo "Category: https://www.reedsail.com/category/软件下载\n";
