#!/bin/bash
set -euo pipefail

echo "=== AgentMarket — One-Click Deploy ==="
echo ""

# Check prerequisites
for cmd in curl docker git; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Error: $cmd not found. Install it first."
        exit 1
    fi
done

# Docker Compose v2 check
if ! docker compose version &>/dev/null; then
    echo "Error: docker compose v2 not found."
    exit 1
fi

REPO_DIR="/opt/agentmarket"

if [ -d "$REPO_DIR" ]; then
    echo "Updating existing installation..."
    cd "$REPO_DIR"
    git pull
else
    echo "Cloning repository..."
    git clone https://github.com/washingtoneimae-dot/agent.git "$REPO_DIR"
    cd "$REPO_DIR"
fi

# .env check
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo ""
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        echo " .env created from .env.example."
        echo " EDIT IT NOW: nano /opt/agentmarket/.env"
        echo " Set DOMAIN, passwords, and API keys."
        echo " Then run: make deploy"
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    else
        echo "Error: No .env or .env.example found."
        exit 1
    fi
    exit 0
fi

# Pull latest images
echo "Pulling Docker images..."
docker compose pull --quiet

# Start services
echo "Starting services..."
docker compose up -d

echo ""
echo "=========================================="
echo " AgentMarket Deployed!"
echo "=========================================="
DOMAIN=$(grep "^DOMAIN=" .env | cut -d= -f2)
echo " URL:  http://${DOMAIN}:80"
echo " API:  http://${DOMAIN}:80/api/v1/health"
echo ""
echo " Check status: docker compose ps"
echo " View logs:    docker compose logs -f"
echo "=========================================="
