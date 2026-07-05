#!/bin/bash
set -euo pipefail

echo "=== Openfield — One-Click Deploy ==="
echo ""

REPO_DIR="/opt/openfield"

if [ -d "$REPO_DIR" ]; then
    echo "Updating existing installation..."
    cd "$REPO_DIR"
    git pull
else
    echo "Cloning repository..."
    git clone https://github.com/washingtoneimae-dot/agent.git "$REPO_DIR"
    cd "$REPO_DIR"
fi

if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo ""
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        echo " .env created from .env.example."
        echo " EDIT IT NOW: nano /opt/openfield/.env"
        echo " Set DOMAIN, passwords, and API keys."
        echo " Then run: make deploy"
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    else
        echo "Error: No .env or .env.example found."
        exit 1
    fi
    exit 0
fi

echo "Pulling Docker images..."
docker compose pull --quiet

echo "Starting services..."
docker compose up -d

echo ""
echo "=========================================="
echo " Openfield Deployed!"
echo "=========================================="
DOMAIN=$(grep "^DOMAIN=" .env | cut -d= -f2)
echo " URL:  http://${DOMAIN}:80"
echo " API:  http://${DOMAIN}:80/api/v1/health"
echo ""
echo " Check status: docker compose ps"
echo " View logs:    docker compose logs -f"
echo "=========================================="
