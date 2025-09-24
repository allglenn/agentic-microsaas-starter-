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

# Terraform commands for different environments
tf.init:
	@echo "Initializing Terraform for all environments..."
	cd infra/terraform/environments/dev && terraform init
	cd infra/terraform/environments/staging && terraform init
	cd infra/terraform/environments/prod && terraform init

tf.init.dev:
	@echo "Initializing Terraform for development..."
	cd infra/terraform/environments/dev && terraform init

tf.init.staging:
	@echo "Initializing Terraform for staging..."
	cd infra/terraform/environments/staging && terraform init

tf.init.prod:
	@echo "Initializing Terraform for production..."
	cd infra/terraform/environments/prod && terraform init

tf.plan.dev:
	@echo "Planning Terraform for development..."
	cd infra/terraform/environments/dev && terraform plan

tf.plan.staging:
	@echo "Planning Terraform for staging..."
	cd infra/terraform/environments/staging && terraform plan

tf.plan.prod:
	@echo "Planning Terraform for production..."
	cd infra/terraform/environments/prod && terraform plan

tf.apply.dev:
	@echo "Applying Terraform for development..."
	cd infra/terraform/environments/dev && terraform apply -auto-approve

tf.apply.staging:
	@echo "Applying Terraform for staging..."
	cd infra/terraform/environments/staging && terraform apply -auto-approve

tf.apply.prod:
	@echo "Applying Terraform for production..."
	cd infra/terraform/environments/prod && terraform apply -auto-approve

tf.destroy.dev:
	@echo "Destroying Terraform resources for development..."
	cd infra/terraform/environments/dev && terraform destroy -auto-approve

tf.destroy.staging:
	@echo "Destroying Terraform resources for staging..."
	cd infra/terraform/environments/staging && terraform destroy -auto-approve

tf.destroy.prod:
	@echo "Destroying Terraform resources for production..."
	cd infra/terraform/environments/prod && terraform destroy -auto-approve

# Legacy commands for backward compatibility
tf.apply:
	@echo "Please use environment-specific commands: tf.apply.dev, tf.apply.staging, or tf.apply.prod"

tf.destroy:
	@echo "Please use environment-specific commands: tf.destroy.dev, tf.destroy.staging, or tf.destroy.prod"

# Cloud Run deployment commands for different environments
cr.deploy.dev:
	@echo "Deploying to Google Cloud Run (Development)..."
	@echo "Building and pushing images..."
	gcloud builds submit --tag gcr.io/agentic-microsaas-dev/web apps/web
	gcloud builds submit --tag gcr.io/agentic-microsaas-dev/api apps/api
	gcloud builds submit --tag gcr.io/agentic-microsaas-dev/agent apps/agent
	@echo "Deploying services..."
	gcloud run deploy agentic-microsaas-dev-web --image gcr.io/agentic-microsaas-dev/web --project=agentic-microsaas-dev --region=$(REGION) --allow-unauthenticated
	gcloud run deploy agentic-microsaas-dev-api --image gcr.io/agentic-microsaas-dev/api --project=agentic-microsaas-dev --region=$(REGION)
	gcloud run deploy agentic-microsaas-dev-agent --image gcr.io/agentic-microsaas-dev/agent --project=agentic-microsaas-dev --region=$(REGION)

cr.deploy.staging:
	@echo "Deploying to Google Cloud Run (Staging)..."
	@echo "Building and pushing images..."
	gcloud builds submit --tag gcr.io/agentic-microsaas-staging/web apps/web
	gcloud builds submit --tag gcr.io/agentic-microsaas-staging/api apps/api
	gcloud builds submit --tag gcr.io/agentic-microsaas-staging/agent apps/agent
	@echo "Deploying services..."
	gcloud run deploy agentic-microsaas-staging-web --image gcr.io/agentic-microsaas-staging/web --project=agentic-microsaas-staging --region=$(REGION) --allow-unauthenticated
	gcloud run deploy agentic-microsaas-staging-api --image gcr.io/agentic-microsaas-staging/api --project=agentic-microsaas-staging --region=$(REGION)
	gcloud run deploy agentic-microsaas-staging-agent --image gcr.io/agentic-microsaas-staging/agent --project=agentic-microsaas-staging --region=$(REGION)

cr.deploy.prod:
	@echo "Deploying to Google Cloud Run (Production)..."
	@echo "Building and pushing images..."
	gcloud builds submit --tag gcr.io/agentic-microsaas-prod/web apps/web
	gcloud builds submit --tag gcr.io/agentic-microsaas-prod/api apps/api
	gcloud builds submit --tag gcr.io/agentic-microsaas-prod/agent apps/agent
	@echo "Deploying services..."
	gcloud run deploy agentic-microsaas-prod-web --image gcr.io/agentic-microsaas-prod/web --project=agentic-microsaas-prod --region=$(REGION) --allow-unauthenticated
	gcloud run deploy agentic-microsaas-prod-api --image gcr.io/agentic-microsaas-prod/api --project=agentic-microsaas-prod --region=$(REGION)
	gcloud run deploy agentic-microsaas-prod-agent --image gcr.io/agentic-microsaas-prod/agent --project=agentic-microsaas-prod --region=$(REGION)

# Legacy command for backward compatibility
cr.deploy:
	@echo "Please use environment-specific commands: cr.deploy.dev, cr.deploy.staging, or cr.deploy.prod"

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
	@echo ""
	@echo "Local Development:"
	@echo "  dev.up      - Start local infrastructure (PostgreSQL + Redis)"
	@echo "  web.dev     - Start Next.js development server"
	@echo "  api.dev     - Start FastAPI development server"
	@echo "  agent.dev   - Start Celery worker"
	@echo ""
	@echo "Terraform (Environment-specific):"
	@echo "  tf.init.dev     - Initialize Terraform for development"
	@echo "  tf.init.staging - Initialize Terraform for staging"
	@echo "  tf.init.prod    - Initialize Terraform for production"
	@echo "  tf.plan.dev     - Plan Terraform changes for development"
	@echo "  tf.plan.staging - Plan Terraform changes for staging"
	@echo "  tf.plan.prod    - Plan Terraform changes for production"
	@echo "  tf.apply.dev    - Apply Terraform for development"
	@echo "  tf.apply.staging- Apply Terraform for staging"
	@echo "  tf.apply.prod   - Apply Terraform for production"
	@echo "  tf.destroy.dev  - Destroy development resources"
	@echo "  tf.destroy.staging - Destroy staging resources"
	@echo "  tf.destroy.prod - Destroy production resources"
	@echo ""
	@echo "Cloud Run Deployment:"
	@echo "  cr.deploy.dev    - Deploy to development environment"
	@echo "  cr.deploy.staging- Deploy to staging environment"
	@echo "  cr.deploy.prod   - Deploy to production environment"
	@echo ""
	@echo "Utilities:"
	@echo "  sql.init    - Initialize database with pgvector"
	@echo "  fmt         - Format code"
	@echo "  clean       - Clean up Docker containers and volumes"
	@echo "  install     - Install all dependencies"
	@echo "  test        - Run tests"
	@echo "  help        - Show this help message"