# Production Environment
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
    prefix = "prod"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Local variables for prod environment
locals {
  environment = "prod"
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
  db_tier             = var.prod_db_tier
  db_password         = var.db_password
  enable_public_ip    = false
  deletion_protection = true
  redis_tier          = "STANDARD_HA"
  redis_memory_size   = 4
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
  max_instances        = 100
  min_instances        = 2
  cpu_limit            = "2000m"
  memory_limit         = "1Gi"
}

# Storage module
module "storage" {
  source = "../../modules/storage"

  project_id        = var.project_id
  environment       = local.environment
  region            = var.region
  force_destroy     = false
  enable_versioning = true
  lifecycle_age     = 90
  cors_origins      = ["https://agentic-microsaas.com", "https://www.agentic-microsaas.com"]
}

# IAM bindings
resource "google_cloud_run_service_iam_member" "web_public" {
  service  = module.compute.web_service_name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Monitoring and alerting
resource "google_monitoring_notification_channel" "email" {
  display_name = "Email Notification Channel"
  type         = "email"

  labels = {
    email_address = var.alert_email
  }
}

resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "High Error Rate Alert"
  combiner     = "OR"

  conditions {
    display_name = "Error rate condition"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.05

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
        group_by_fields    = ["resource.label.service_name"]
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]
}
