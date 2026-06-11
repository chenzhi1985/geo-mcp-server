#!/bin/bash
# GEO MCP Server — 部署支付页到 reedsail.com
# 运行: bash deploy.sh

SSH_HOST="43.132.232.148"
SSH_USER="ubuntu"
SSH_KEY="$HOME/.ssh/id_ed25519"
SSH="ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST"

echo "🚀 部署 GEO MCP 支付页到 reedsail.com..."
echo ""

# 1. 上传支付页面
echo "📤 上传支付页面..."
$SSH "sudo mkdir -p /var/www/geo-pro"
scp -i "$SSH_KEY" -r payment/wechat/* "$SSH_USER@$SSH_HOST:/tmp/geo-pro/"
$SSH "sudo cp -r /tmp/geo-pro/* /var/www/geo-pro/ && sudo rm -rf /tmp/geo-pro"
$SSH "sudo chown -R www-data:www-data /var/www/geo-pro/"
echo "✅ 支付页面已上传"

# 2. 配置 Nginx
echo ""
echo "📝 配置 Nginx..."
NGINX_CONF="/etc/nginx/sites-available/reedsail.com"
$SSH "sudo grep -q '/geo-pro/' $NGINX_CONF || sudo sed -i '/server_name/i\\
    location /geo-pro/ {\\
        root /var/www/geo-pro;\\
        index index.html;\\
        try_files \$uri \$uri/ /geo-pro/index.html;\\
    }\\
' $NGINX_CONF"

$SSH "sudo nginx -t && sudo systemctl reload nginx"
echo "✅ Nginx 已配置"

# 3. 验证
echo ""
echo "🔍 验证部署..."
sleep 2
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://www.reedsail.com/geo-pro/)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ https://www.reedsail.com/geo-pro/ 可以访问了！"
else
    echo "⚠️  HTTP $HTTP_CODE — 可能需要等几秒"
fi

echo ""
echo "🎉 部署完成！"
echo "   购买页面: https://www.reedsail.com/geo-pro/"
echo ""
echo "📋 后续步骤:"
echo "   1. 替换 payment/wechat/index.html 中的微信收款码"
echo "   2. 启动支付 API: uvicorn payment.api:app --port 8899 &"
echo "   3. 签发 License: python payment/admin.py issue pro 用户邮箱"
