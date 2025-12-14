#!/bin/bash
# Setup script for SOCAR API with nginx reverse proxy

set -e

echo "🔧 Setting up SOCAR API with nginx reverse proxy..."

# ============================================================================
# 1. Create nginx configuration
# ============================================================================

echo "📝 Creating nginx configuration..."

sudo tee /etc/nginx/sites-available/socar-api > /dev/null <<'EOF'
upstream socar_backend {
    server 127.0.0.1:9000;
}

server {
    listen 80;
    server_name beatbyteai-vm-ip.polandcentral.cloudapp.azure.com;

    client_max_body_size 100M;

    # Logging
    access_log /var/log/nginx/socar-api-access.log;
    error_log /var/log/nginx/socar-api-error.log;

    # Root path - proxy to backend
    location / {
        proxy_pass http://socar_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running requests
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://socar_backend;
        access_log off;
    }
}
EOF

echo "✅ Nginx configuration created"

# ============================================================================
# 2. Enable the site
# ============================================================================

echo "🔗 Enabling nginx site..."

if [ ! -L /etc/nginx/sites-enabled/socar-api ]; then
    sudo ln -s /etc/nginx/sites-available/socar-api /etc/nginx/sites-enabled/socar-api
    echo "✅ Site symlink created"
else
    echo "✅ Site already enabled"
fi

# ============================================================================
# 3. Test nginx configuration
# ============================================================================

echo "🧪 Testing nginx configuration..."
sudo nginx -t

# ============================================================================
# 4. Restart nginx
# ============================================================================

echo "🔄 Restarting nginx..."
sudo systemctl restart nginx

echo "✅ Nginx restarted"

# ============================================================================
# 5. Display information
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          SOCAR API Setup Complete                             ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║ Public URL: http://beatbyteai-vm-ip.polandcentral.cloudapp.azure.com"
echo "║ Backend:    http://127.0.0.1:9000"
echo "║ Proxy:      nginx (port 80)"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║ Start the app with:                                           ║"
echo "║   python main.py --port 9000                                  ║"
echo "║ Or:                                                           ║"
echo "║   uv run python main.py --port 9000                           ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║ Logs:                                                         ║"
echo "║   Nginx access: /var/log/nginx/socar-api-access.log           ║"
echo "║   Nginx error:  /var/log/nginx/socar-api-error.log            ║"
echo "║   sudo tail -f /var/log/nginx/socar-api-access.log            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
