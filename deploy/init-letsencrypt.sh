#!/bin/bash
set -euo pipefail

DOMAIN="${DOMAIN:-}"
EMAIL="${LETSENCRYPT_EMAIL:-admin@example.com}"

if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "localhost" ]; then
    echo "DOMAIN not set or is localhost. Skipping Let's Encrypt."
    exit 0
fi

echo "=== Let's Encrypt SSL for $DOMAIN ==="

mkdir -p docker/nginx/certbot_www
docker compose up -d nginx
sleep 2

docker compose run --rm --entrypoint "" certbot/certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    || echo "Certbot failed. Check DNS records for $DOMAIN"

CERT_DIR="/etc/letsencrypt/live/$DOMAIN"
if [ -d "$CERT_DIR" ]; then
    mkdir -p docker/nginx/ssl
    cp "$CERT_DIR/fullchain.pem" docker/nginx/ssl/
    cp "$CERT_DIR/privkey.pem" docker/nginx/ssl/
    echo "Certificates installed."
fi

echo "0 3 * * * root docker compose -f /opt/agentmarket/docker-compose.yml run --rm certbot/certbot renew && docker compose restart nginx" \
    | sudo tee /etc/cron.d/agentmarket-certbot
echo "Auto-renewal cron installed."
