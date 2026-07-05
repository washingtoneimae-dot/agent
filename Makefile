.PHONY: up down logs build deploy shell-db shell-api reset seed

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

build:
	docker compose build --no-cache

deploy: up
	@echo "=========================================="
	@echo " AgentMarket deployed!"
	@echo " Frontend: http://$$(grep DOMAIN .env | cut -d= -f2):3000"
	@echo " API:      http://$$(grep DOMAIN .env | cut -d= -f2):8000/api/v1/health"
	@echo "=========================================="

shell-db:
	docker compose exec postgres psql -U $(shell grep DB_USER .env | cut -d= -f2) -d agentmarket

shell-api:
	docker compose exec api /bin/bash

reset:
	docker compose down -v
	docker compose up -d

seed:
	docker compose exec api python -m app.seed

status:
	docker compose ps

# Production helpers
prod-logs:
	docker compose logs -f --tail=100

prod-restart:
	docker compose restart

prod-update:
	docker compose pull
	docker compose up -d --build
