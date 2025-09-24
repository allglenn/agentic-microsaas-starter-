# Development Environment
terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }

  backend "gcs" {
    bucket = "agentic-microsaas-terraform-state"
    prefix = "dev"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Local variables for dev environment
locals {
  environment = "dev"
  common_tags = {
    Environment = local.environment
    Project     = var.project_id
    ManagedBy   = "terraform"
  }
}

# Database module
module "database" {
  source = "../../modules/database"

  project_id          = var.project_id
  environment         = local.environment
  region              = var.region
  db_tier             = var.dev_db_tier
  db_password         = var.db_password
  enable_public_ip    = true
  deletion_protection = false
  redis_tier          = "BASIC"
  redis_memory_size   = 1
}

# Compute module
module "compute" {
  source = "../../modules/compute"

  project_id           = var.project_id
  environment          = local.environment
  region               = var.region
  registry_url         = var.registry_url
  image_tag            = var.image_tag
  database_url         = "postgresql://user:${var.db_password}@${module.database.database_private_ip}:5432/agentic_microsaas"
  redis_url            = "redis://${module.database.redis_host}:${module.database.redis_port}"
  nextauth_url         = var.nextauth_url
  nextauth_secret      = var.nextauth_secret
  google_client_id     = var.google_client_id
  google_client_secret = var.google_client_secret
  api_secret_key       = var.api_secret_key
  openai_api_key       = var.openai_api_key
  max_instances        = 3
  min_instances        = 0
  cpu_limit            = "500m"
  memory_limit         = "256Mi"
}

# Storage module
module "storage" {
  source = "../../modules/storage"

  project_id        = var.project_id
  environment       = local.environment
  region            = var.region
  force_destroy     = true
  enable_versioning = false
  lifecycle_age     = 7
  cors_origins      = ["http://localhost:3000", "https://dev.agentic-microsaas.com"]
}

# IAM bindings
resource "google_cloud_run_service_iam_member" "web_public" {
  service  = module.compute.web_service_name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
