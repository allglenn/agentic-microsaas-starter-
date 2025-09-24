# Staging Environment
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
    prefix = "staging"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Local variables for staging environment
locals {
  environment = "staging"
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
  db_tier             = var.staging_db_tier
  db_password         = var.db_password
  enable_public_ip    = false
  deletion_protection = false
  redis_tier          = "STANDARD_HA"
  redis_memory_size   = 2
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
  max_instances        = 10
  min_instances        = 1
  cpu_limit            = "1000m"
  memory_limit         = "512Mi"
}

# Storage module
module "storage" {
  source = "../../modules/storage"

  project_id        = var.project_id
  environment       = local.environment
  region            = var.region
  force_destroy     = true
  enable_versioning = true
  lifecycle_age     = 30
  cors_origins      = ["https://staging.agentic-microsaas.com"]
}

# IAM bindings
resource "google_cloud_run_service_iam_member" "web_public" {
  service  = module.compute.web_service_name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
