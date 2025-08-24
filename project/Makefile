# AI Cache Proxy - Makefile
# Modern development and deployment commands

.PHONY: help build up down restart logs clean test lint format docker-build docker-push

# Default target
help: ## Show this help message
	@echo "🚀 AI Cache Proxy - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development Commands
build: ## Build all Docker images
	@echo "🔨 Building Docker images..."
	docker-compose build --no-cache

up: ## Start all services
	@echo "🚀 Starting AI Cache Proxy services..."
	docker-compose up -d

up-build: ## Build and start all services
	@echo "🔨 Building and starting services..."
	docker-compose up -d --build

down: ## Stop all services
	@echo "🛑 Stopping services..."
	docker-compose down

restart: ## Restart all services
	@echo "🔄 Restarting services..."
	docker-compose restart

logs: ## Show logs from all services
	@echo "📋 Showing logs..."
	docker-compose logs -f

logs-proxy: ## Show proxy service logs
	@echo "📋 Showing proxy logs..."
	docker-compose logs -f proxy

logs-analyzer: ## Show AI analyzer logs
	@echo "📋 Showing analyzer logs..."
	docker-compose logs -f proxy-analyzer

logs-redis: ## Show Redis logs
	@echo "📋 Showing Redis logs..."
	docker-compose logs -f redis

# Monitoring Commands
monitor: ## Start monitoring services (Prometheus + Grafana)
	@echo "📊 Starting monitoring services..."
	docker-compose up -d prometheus grafana

monitor-logs: ## Show monitoring logs
	@echo "📋 Showing monitoring logs..."
	docker-compose logs -f prometheus grafana

# Testing Commands
test: ## Run all tests
	@echo "🧪 Running tests..."
	@echo "Testing Go proxy..."
	cd ../go-proxy && go test ./...
	@echo "Testing Python service..."
	cd ../llama-service && python -m pytest tests/ -v

test-proxy: ## Test proxy endpoints
	@echo "🧪 Testing proxy endpoints..."
	@echo "Testing health endpoint..."
	curl -f http://localhost:8080/health
	@echo "Testing analytics endpoint..."
	curl -f http://localhost:8080/analytics
	@echo "Testing cache stats endpoint..."
	curl -f http://localhost:8080/cache/stats

# Maintenance Commands
clean: ## Clean up Docker resources
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	docker volume prune -f

clean-all: ## Clean everything including images
	@echo "🧹 Cleaning everything..."
	docker-compose down -v --remove-orphans
	docker system prune -af
	docker volume prune -f

# Development Setup
setup: ## Initial setup and configuration
	@echo "⚙️ Setting up development environment..."
	@echo "Creating necessary directories..."
	mkdir -p ../monitoring/grafana/dashboards
	mkdir -p ../monitoring/grafana/datasources
	@echo "Setting up environment variables..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file..."; \
		echo "SERVER_PORT=8080" > .env; \
		echo "REDIS_ADDR=redis:6379" >> .env; \
		echo "LOG_LEVEL=info" >> .env; \
		echo "AI_ENABLED=true" >> .env; \
	fi
	@echo "✅ Setup complete!"

# Performance Commands
benchmark: ## Run performance benchmarks
	@echo "⚡ Running performance benchmarks..."
	@echo "Testing proxy performance..."
	ab -n 1000 -c 10 http://localhost:8080/health
	@echo "Testing cache performance..."
	ab -n 1000 -c 10 http://localhost:8080/analytics

# Security Commands
security-scan: ## Run security scans
	@echo "🔒 Running security scans..."
	docker-compose exec proxy-analyzer bandit -r /app
	docker-compose exec proxy gosec ./...

# Backup and Restore
backup: ## Backup Redis data
	@echo "💾 Creating backup..."
	docker-compose exec redis redis-cli BGSAVE
	@echo "Backup saved to Redis dump.rdb"

restore: ## Restore from backup (requires backup file)
	@echo "📥 Restoring from backup..."
	@echo "Please place your backup file in the project directory and run:"
	@echo "docker-compose exec redis redis-cli FLUSHALL"
	@echo "docker cp backup.rdb ai-cache-proxy_redis_1:/data/dump.rdb"

# Production Commands
prod-build: ## Build production images
	@echo "🏭 Building production images..."
	docker-compose -f docker-compose.prod.yml build

prod-up: ## Deploy to production
	@echo "🚀 Deploying to production..."
	docker-compose -f docker-compose.prod.yml up -d

prod-down: ## Stop production deployment
	@echo "🛑 Stopping production deployment..."
	docker-compose -f docker-compose.prod.yml down

# Utility Commands
status: ## Show service status
	@echo "📊 Service Status:"
	docker-compose ps

shell-proxy: ## Open shell in proxy container
	@echo "🐚 Opening shell in proxy container..."
	docker-compose exec proxy sh

shell-analyzer: ## Open shell in analyzer container
	@echo "🐚 Opening shell in analyzer container..."
	docker-compose exec proxy-analyzer bash

shell-redis: ## Open Redis CLI
	@echo "🐚 Opening Redis CLI..."
	docker-compose exec redis redis-cli

# Quick Start
quick-start: setup up ## Quick start: setup and start services
	@echo "✅ AI Cache Proxy is ready!"
	@echo "🌐 Dashboard: http://localhost:8080/dashboard"
	@echo "📊 Grafana: http://localhost:3000 (admin/admin)"
	@echo "📈 Prometheus: http://localhost:9090"
	@echo "🔍 Health Check: http://localhost:8080/health"

# Development workflow
dev: down clean up logs ## Development workflow: clean, rebuild, and start with logs

