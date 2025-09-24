SHELL := /bin/bash
PROJECT_ID := agentic-microsaas
REGION := europe-west1

.PHONY: dev.up web.dev api.dev agent.dev tf.init tf.apply cr.deploy sql.init fmt clean

dev.up:
	@echo "Starting local infrastructure with Docker Compose..."
	docker-compose up -d postgres redis
	@echo "Waiting for services to be ready..."
	sleep 10
	@echo "Infrastructure is ready!"

web.dev:
	@echo "Starting Next.js development server..."
	cd apps/web && npm install && npm run dev

api.dev:
	@echo "Starting FastAPI development server..."
	cd apps/api && pip install -r requirements.txt && uvicorn main:app --reload --host 0.0.0.0 --port 8000

agent.dev:
	@echo "Starting Celery worker..."
	cd apps/agent && pip install -r requirements.txt && celery -A worker worker --loglevel=info

tf.init:
	@echo "Initializing Terraform..."
	cd infra/terraform && terraform init

tf.apply:
	@echo "Applying Terraform configuration..."
	cd infra/terraform && terraform apply -auto-approve -var='project_id=$(PROJECT_ID)' -var='region=$(REGION)'

tf.destroy:
	@echo "Destroying Terraform resources..."
	cd infra/terraform && terraform destroy -auto-approve -var='project_id=$(PROJECT_ID)' -var='region=$(REGION)'

cr.deploy:
	@echo "Deploying to Google Cloud Run..."
	@echo "Building and pushing images..."
	gcloud builds submit --tag gcr.io/$(PROJECT_ID)/web apps/web
	gcloud builds submit --tag gcr.io/$(PROJECT_ID)/api apps/api
	gcloud builds submit --tag gcr.io/$(PROJECT_ID)/agent apps/agent
	@echo "Deploying services..."
	gcloud run deploy web --image gcr.io/$(PROJECT_ID)/web --project=$(PROJECT_ID) --region=$(REGION) --allow-unauthenticated
	gcloud run deploy api --image gcr.io/$(PROJECT_ID)/api --project=$(PROJECT_ID) --region=$(REGION)
	gcloud run deploy agent --image gcr.io/$(PROJECT_ID)/agent --project=$(PROJECT_ID) --region=$(REGION)

sql.init:
	@echo "Initializing database with pgvector extension..."
	@echo "Connect to your database and run:"
	@echo "psql -c \"CREATE EXTENSION IF NOT EXISTS vector;\""

fmt:
	@echo "Formatting code..."
	cd apps/api && black . && isort .
	cd apps/agent && black . && isort .
	cd apps/web && npm run lint

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	docker system prune -f

install:
	@echo "Installing dependencies..."
	cd apps/web && npm install
	cd apps/api && pip install -r requirements.txt
	cd apps/agent && pip install -r requirements.txt

test:
	@echo "Running tests..."
	cd apps/api && python -m pytest
	cd apps/agent && python -m pytest

help:
	@echo "Available commands:"
	@echo "  dev.up      - Start local infrastructure (PostgreSQL + Redis)"
	@echo "  web.dev     - Start Next.js development server"
	@echo "  api.dev     - Start FastAPI development server"
	@echo "  agent.dev   - Start Celery worker"
	@echo "  tf.init     - Initialize Terraform"
	@echo "  tf.apply    - Apply Terraform configuration"
	@echo "  tf.destroy  - Destroy Terraform resources"
	@echo "  cr.deploy   - Deploy to Google Cloud Run"
	@echo "  sql.init    - Initialize database with pgvector"
	@echo "  fmt         - Format code"
	@echo "  clean       - Clean up Docker containers and volumes"
	@echo "  install     - Install all dependencies"
	@echo "  test        - Run tests"
	@echo "  help        - Show this help message"